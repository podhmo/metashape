import typing as t
from .marker import mark  # noqa

# TODO: rename to prepare.py?

T = t.TypeVar("T")
MetaData = t.Optional[t.Dict[str, t.Any]]


class _Field(t.Generic[T]):
    default: T
    metadata: t.Optional[MetaData]

    def __init__(self, default: T, *, metadata: t.Optional[MetaData] = None):
        self.default = default
        self.metadata = metadata

    def __get__(self, obj, type=None) -> T:
        return self.default


def field(*, default: T, metadata: t.Dict[str, t.Any] = None) -> T:
    return t.cast(T, _Field(default, metadata=metadata))  # xxx: HACK


def get_metadata(cls: t.Type[t.Any], name: str) -> t.Optional[MetaData]:
    prop = cls.__dict__.get(name)
    if prop is None:
        return None
    return prop.metadata
