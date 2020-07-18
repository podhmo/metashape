from __future__ import annotations
import typing as t
import warnings
import logging
from metashape.marker import guess_mark
from metashape import constants
from metashape.types import MetaData, Kind, Member, IteratePropsFunc
from metashape._access import iterate_props  # TODO: move
from metashape._dataclass import iterate_props as iterate_props_for_dataclass
from metashape._dataclass import is_dataclass
from metashape.typeinfo import TypeInfo
from .resolver import Resolver
from .config import Config


logger = logging.getLogger(__name__)


class Walker:
    resolver: Resolver

    def __init__(
        self, members: t.List[t.Any], *, config: Config, resolver: Resolver
    ) -> None:
        self.resolver = resolver
        self.config = config
        self._members = t.cast(t.List[Member], members)  # xxx

    def for_type(self, m: Member) -> TypeWalker:
        warnings.warn("depreacated. use Walker.get_type_walker() or Walker.walk_fields(), instead of Walker.for_type()")
        # TODO: explicitly is better?
        fn = iterate_props_for_dataclass if is_dataclass(m) else iterate_props
        return TypeWalker(m, parent=self, iterate_props=fn)

    def get_type_walker(self, m: Member) -> TypeWalker:
        fn = iterate_props_for_dataclass if is_dataclass(m) else iterate_props
        return TypeWalker(m, parent=self, iterate_props=fn)

    def walk_fields(
        self, m: Member, *, ignore_private: t.Optional[bool] = None
    ) -> t.Iterable[t.Tuple[str, TypeInfo, MetaData]]:
        return self.get_type_walker(m).walk(ignore_private=ignore_private)

    def append(self, m: Member) -> None:
        self.config.q.append(m)

    def __len__(self) -> int:
        return len(self._members)

    def walk(
        self,
        *,
        kinds: t.Sequence[t.Optional[Kind]] = ["object"],
        ignore_private: t.Optional[bool] = None,
        nocheck: bool = False,
    ) -> t.Iterable[Member]:
        resolver = self.resolver
        cfg = self.config
        if ignore_private is None:
            ignore_private = cfg.option.ignore_private

        for m in self._members:
            self.config.q.append(m)

        while True:
            try:
                m = cfg.q.popleft()
            except IndexError:
                break

            name = resolver.resolve_typename(m)
            if not nocheck:
                if not name:
                    continue
                if ignore_private:
                    if name.startswith("_"):
                        continue

                if guess_mark(m) not in kinds:
                    continue
            logger.info("walk type: %r", m)
            yield m


class TypeWalker:
    def __init__(
        self,
        typ: t.Type[t.Any],
        *,
        parent: Walker,
        iterate_props: IteratePropsFunc = iterate_props,
    ):
        self.typ = typ
        self.parent = parent
        self.iterate_props = iterate_props

    def walk(
        self, *, ignore_private: t.Optional[bool] = None
    ) -> t.Iterable[t.Tuple[str, TypeInfo, MetaData]]:
        if ignore_private is None:
            cfg = self.parent.config
            ignore_private = cfg.option.ignore_private

        resolver = self.parent.resolver
        for name, field_type, metadata in self.iterate_props(
            self.typ, ignore_private=ignore_private
        ):
            if metadata is None:
                metadata = {}

            logger.info(
                "walk prop: 	name=%r	type=%r	keys(metadata)=%s",
                name,
                field_type,
                metadata.keys(),
            )
            info = resolver.resolve_typeinfo(field_type)
            logger.debug("walk prop: 	info=%r", info)

            # handle default
            if hasattr(self.typ, name):
                metadata[constants.DEFAULT] = getattr(self.typ, name)
            yield name, info, metadata
