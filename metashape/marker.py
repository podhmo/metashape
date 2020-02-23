import typing as t
import weakref
from .types import T, Kind

_registry = weakref.WeakKeyDictionary()  # type: t.Dict[object, Kind]


def is_marked(
    cls: t.Type[t.Any], *, _registgry: t.Dict[object, Kind] = _registry,
) -> bool:
    return _registry.get(cls) is not None


def guess_mark(
    cls: t.Type[t.Any], *, _registgry: t.Dict[object, Kind] = _registry,
) -> t.Optional[Kind]:
    return _registry.get(cls)


def mark(
    cls: t.Type[T],
    *,
    kind: Kind = "object",
    _registgry: t.Dict[object, Kind] = _registry,
) -> t.Type[T]:
    if is_marked(cls):
        return cls
    _registry[cls] = kind
    return cls


# TODO: remove
# def is_marked(cls: t.Type[t.Any]) -> bool:
#     return getattr(cls, "_metashape_mark", None) is not None


# def guess_mark(cls: t.Type[t.Any]) -> t.Optional[Kind]:
#     return getattr(cls, "_metashape_mark", None)  # type: ignore


# def mark(cls: t.Type[T], *, kind: Kind = "object") -> t.Type[T]:
#     if is_marked(cls):
#         return cls
#     setattr(cls, "_metashape_mark", kind)
#     return cls
