import typing as t
from .marker import mark  # noqa
from .types import MetaData, T

# TODO: rename to prepare.py?


class _Field(t.Generic[T]):
    default: T
    metadata: t.Optional[MetaData]

    def __init__(self, default: T, *, metadata: t.Optional[MetaData] = None):
        self.default = default
        self.metadata = metadata

    def __get__(self, obj: object, type: t.Optional[t.Type[t.Any]] = None) -> T:
        return self.default


def field(*, default: T, metadata: t.Optional[t.Dict[str, t.Any]] = None) -> T:
    return t.cast(T, _Field(default, metadata=metadata))  # xxx: HACK


def get_metadata(cls: t.Type[t.Any], name: str) -> t.Optional[MetaData]:
    prop = cls.__dict__.get(name)
    if prop is None:
        return None
    return getattr(prop, "metadata", None)  # type: ignore
