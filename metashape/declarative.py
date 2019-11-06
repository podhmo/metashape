import typing as t
from .marker import mark  # noqa F401
from .types import MetaData, T
from .constants import ORIGINAL_NAME  # noqa F401

shape = mark  # this is better name?


class _Field(t.Generic[T]):
    default: T
    metadata: t.Optional[MetaData]

    def __init__(self, default: T, *, metadata: t.Optional[MetaData] = None):
        self.default = default
        self.metadata = metadata

    def __get__(self, obj: object, type: t.Optional[t.Type[t.Any]] = None) -> T:
        return self.default


def field(default: T, *, metadata: t.Optional[t.Dict[str, t.Any]] = None) -> T:
    return t.cast(T, _Field(default, metadata=metadata))  # xxx: HACK
