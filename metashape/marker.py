import typing as t
from .types import T, Kind


# TODO: remove
def is_marked(cls: t.Type[t.Any]) -> bool:
    return getattr(cls, "_metashape_mark", None) is not None


def guess_mark(cls: t.Type[t.Any]) -> t.Optional[Kind]:
    return getattr(cls, "_metashape_mark", None)  # type: ignore


def mark(cls: t.Type[T], *, kind: Kind = "object") -> t.Type[T]:
    if is_marked(cls):
        return cls
    setattr(cls, "_metashape_mark", kind)
    return cls
