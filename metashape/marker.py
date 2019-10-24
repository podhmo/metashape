import typing as t
from .types import T, Kind


# TODO: remove
def is_marked(cls: t.Type[T]) -> bool:
    return getattr(cls, "_metashape_mark", None) is not None


def guess_mark(cls: t.Type[T]) -> t.Optional[Kind]:
    return getattr(cls, "_metashape_mark", None)


def mark(cls: t.Type[T], *, kind: Kind = "object") -> t.Type[T]:
    if is_marked(cls):
        return cls
    setattr(cls, "_metashape_mark", kind)
    return cls
