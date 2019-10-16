import typing as t
from .types import T


# TODO: remove


def is_marked(cls: t.Type[T]) -> bool:
    return hasattr(cls, "_shape_mark")


def mark(cls: t.Type[T]) -> t.Type[T]:
    if is_marked(cls):
        return cls
    setattr(cls, "_shape_mark", True)
    return cls
