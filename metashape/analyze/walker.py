from __future__ import annotations
import typing as t
import logging
from metashape.marker import guess_mark
from metashape.constants import ORIGINAL_NAME
from metashape.types import MetaData, Kind, Member
from metashape._access import iterate_props  # TODO: move
from .typeinfo import TypeInfo
from .resolver import Resolver
from .context import Context


logger = logging.getLogger(__name__)


class ModuleWalker:
    resolver: Resolver

    def __init__(
        self, members: t.List[t.Any], *, context: Context, resolver: Resolver
    ) -> None:
        self.resolver = resolver
        self.context = context
        self._members = t.cast(t.List[Member], members)  # xxx

    def for_type(self, m: Member) -> TypeWalker:
        return TypeWalker(m, parent=self)

    def append(self, m: Member) -> None:
        self.context.q.append(m)

    def __len__(self) -> int:
        return len(self._members)

    def walk(
        self, *, kinds: t.List[Kind] = ["object"], ignore_private: bool = False
    ) -> t.Iterable[Member]:
        ctx = self.context
        for m in self._members:
            self.context.q.append(m)

        while True:
            try:
                m = ctx.q.popleft()
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
            yield m


class TypeWalker:
    def __init__(self, typ: t.Type[t.Any], *, parent: ModuleWalker):
        self.typ = typ
        self.parent = parent

    def walk(
        self, *, ignore_private: bool = False
    ) -> t.Iterable[t.Tuple[str, TypeInfo, t.Optional[MetaData]]]:
        resolver = self.parent.resolver
        try:
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
                info = resolver.resolve_type_info(field_type)
                logger.debug("walk prop: 	info=%r", info)
                if ORIGINAL_NAME in metadata:
                    name = metadata[ORIGINAL_NAME]

                yield name, info, metadata
        except TypeError as e:
            logger.info("iterate props: %r", e)
            return []
