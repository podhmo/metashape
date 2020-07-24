import typing as t
from .types import T, Kind


_mapping: t.Dict[t.Any, Kind] = {}


def is_marked(cls: t.Type[t.Any]) -> bool:
    global _mapping
    return _mapping.get(id(cls)) is not None


def guess_mark(cls: t.Type[t.Any]) -> t.Optional[Kind]:
    global _mapping
    return _mapping.get(id(cls))


def mark(cls: t.Type[T], *, kind: Kind = "object") -> t.Type[T]:
    global _mapping
    if is_marked(cls):
        return cls
    _mapping[id(cls)] = kind
    return cls
