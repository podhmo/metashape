from __future__ import annotations
import typing as t
import logging
import dataclasses
from collections import defaultdict
from metashape.marker import guess_mark
from metashape import constants
from metashape.types import MetaData, Kind, Member, IteratePropsFunc
from metashape._access import iterate_props  # TODO: move
from metashape._dataclass import iterate_props as iterate_props_for_dataclass
from metashape._dataclass import is_dataclass
from .typeinfo import TypeInfo
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
        # TODO: explicitly is better?
        fn = iterate_props_for_dataclass if is_dataclass(m) else iterate_props
        return TypeWalker(m, parent=self, iterate_props=fn)

    def append(self, m: Member) -> None:
        self.config.q.append(m)

    def __len__(self) -> int:
        return len(self._members)

    def walk(
        self,
        *,
        kinds: t.List[Kind] = ["object"],
        ignore_private: t.Optional[bool] = None
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
            if not name:
                continue
            if ignore_private:
                if name.startswith("_"):
                    continue

            if not guess_mark(m) in kinds:
                continue
            logger.info("walk type: %r", m)
            yield m

    def walked(self, *, kinds: t.List[Kind] = ["object"], ignore_private: bool = False):
        seen: t.Dict[Kind, t.List] = defaultdict(list)
        names: t.Dict[Member, str] = {}
        history: t.List[Member] = []
        resolver = self.resolver

        for m in self.walk(kinds=kinds, ignore_private=ignore_private):
            kind = guess_mark(m)
            names[m] = resolver.resolve_typename(m)
            seen[kind].append(m)
            history.append(m)
        return Walked(seen=seen, names=names, _history=history)


@dataclasses.dataclass(frozen=True)
class Walked:
    seen: t.Dict[Kind, t.List]
    names: t.Dict[Member, str]
    _history: t.List[Member]

    def __iter__(self) -> t.Iterable[Member]:
        return iter(self._history)

    @property
    def enums(self) -> t.Iterable[Member]:
        return iter(self.seen["enum"])

    @property
    def objects(self) -> t.Iterable[Member]:
        return iter(self.seen["object"])

    def get_name(self, m: Member) -> t.Optional[str]:
        return self.names.get(m)


class TypeWalker:
    def __init__(
        self,
        typ: t.Type[t.Any],
        *,
        parent: Walker,
        iterate_props: IteratePropsFunc = iterate_props
    ):
        self.typ = typ
        self.parent = parent
        self.iterate_props = iterate_props

    def walk(
        self, *, ignore_private: t.Optional[bool] = None
    ) -> t.Iterable[t.Tuple[str, TypeInfo, t.Optional[MetaData]]]:
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
            info = resolver.typeinfo.resolve(field_type)
            logger.debug("walk prop: 	info=%r", info)

            # handle default
            if hasattr(self.typ, name):
                metadata[constants.DEFAULT] = getattr(self.typ, name)
            yield name, info, metadata
