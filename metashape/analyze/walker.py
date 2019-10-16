from __future__ import annotations
import typing as t
from collections import deque
from metashape.types import T, MetaData
from metashape.langhelpers import reify
from metashape.declarative import get_metadata  # TODO: move
from .core import Member
from .resolver import Resolver


class Walker:
    resolver: Resolver

    def __init__(self, members: t.List[t.Any], *, resolver: Resolver) -> None:
        self.resolver = resolver
        self._members = t.cast(t.List[Member], members)  # xxx

    def walk_module(self) -> t.List[Member]:
        return self._members

    def walk_type(
        self, m: Member
    ) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
        yield from walk_type(m)

    @reify
    def context(self) -> Context:
        return Context()

    @reify
    def q(self) -> _Queue:
        return _Queue()


class Context:
    def __init__(self, strict: bool = True, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose


class _Queue:
    q: t.Deque[Member]
    seen: t.Set[Member]

    def __init__(self) -> None:
        self.q = deque()
        self.seen = set()

    def append(self, x: Member) -> None:
        self.q.append(x)

    def popleft(self) -> Member:  # raise IndexError
        while True:
            x = self.q.popleft()
            if x in self.seen:
                continue
            self.seen.add(x)
            return x


def walk_type(
    typ: t.Type[t.Any]
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for fieldname, fieldtype in t.get_type_hints(typ).items():
        yield fieldname, fieldtype, get_metadata(typ, fieldname)
