import typing as t
from collections import ChainMap
from dataclasses import fields, Field
from dataclasses import is_dataclass
from .types import MetaData, IteratePropsFunc


def iterate_props(
    typ: t.Type[t.Any], *, ignore_private: bool = True
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for field in fields(typ):  # type: Field[t.Any]
        mutable_state: t.Dict[str, t.Any] = {}
        metadata = ChainMap(mutable_state, field.metadata)
        yield field.name, field.type, metadata


# type assertion
_: IteratePropsFunc = iterate_props

__all__ = ["iterate_props", "is_dataclass", "Field", "fields"]
