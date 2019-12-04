from __future__ import annotations
import typing as t
import logging
from metashape.marker import guess_mark
from metashape import constants
from metashape.types import MetaData, Kind, Member
from metashape._access import iterate_props  # TODO: move
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
        return TypeWalker(m, parent=self)

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

            name = self.resolver.resolve_typename(m)
            if not name:
                continue
            if ignore_private:
                if name.startswith("_"):
                    continue

            if not guess_mark(m) in kinds:
                continue
            logger.info("walk type: %r", m)
            yield m


class TypeWalker:
    def __init__(self, typ: t.Type[t.Any], *, parent: Walker):
        self.typ = typ
        self.parent = parent

    def walk(
        self, *, ignore_private: t.Optional[bool] = None
    ) -> t.Iterable[t.Tuple[str, TypeInfo, t.Optional[MetaData]]]:
        if ignore_private is None:
            cfg = self.parent.config
            ignore_private = cfg.option.ignore_private

        resolver = self.parent.resolver
        for name, field_type, metadata in iterate_props(
            self.typ, ignore_private=ignore_private
        ):
            metadata = metadata or {}
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
