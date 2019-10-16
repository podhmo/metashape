import typing as t
from metashape.declarative import MetaData, get_metadata  # TODO: move
from .core import Member


class Walker:
    def __init__(self, members: t.List[t.Any]) -> None:
        self._members = t.cast(t.List[Member], members)  # xxx

    def walk_module(self) -> t.List[Member]:
        return self._members

    def walk_type(
        self, m: Member
    ) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
        yield from walk_type(m)


def walk_type(
    typ: t.Type[t.Any]
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for fieldname, fieldtype in t.get_type_hints(typ).items():
        yield fieldname, fieldtype, get_metadata(typ, fieldname)
