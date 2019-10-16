from __future__ import annotations
import typing as t
from metashape.types import MetaData
from metashape.langhelpers import reify
from metashape.declarative import get_metadata  # TODO: move
from .core import Member
from .resolver import Resolver
from .context import Context


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


def walk_type(
    typ: t.Type[t.Any]
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for fieldname, fieldtype in t.get_type_hints(typ).items():
        yield fieldname, fieldtype, get_metadata(typ, fieldname)
