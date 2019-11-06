from __future__ import annotations
import typing as t
import logging
from metashape.marker import guess_mark
from metashape.types import MetaData, Kind, Member
from metashape.langhelpers import reify
from metashape._access import iterate_props  # TODO: move
from .resolver import Resolver
from .context import Context


logger = logging.getLogger(__name__)


class ModuleWalker:
    resolver: Resolver

    def __init__(self, members: t.List[t.Any], *, resolver: Resolver) -> None:
        self.resolver = resolver
        self._members = t.cast(t.List[Member], members)  # xxx

    def for_type(self, m: Member) -> TypeWalker:
        return TypeWalker(m, parent=self)

    @reify
    def context(self) -> Context:
        return Context()

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
                if ignore_private and m.__name__.startswith("_"):
                    continue
                if guess_mark(m) in kinds:
                    yield m
            except IndexError:
                break


class TypeWalker:
    def __init__(self, typ: t.Type[t.Any], *, parent: ModuleWalker):
        self.typ = typ
        self.parent = parent

    def walk(self) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
        return iterate_props(self.typ)
