from __future__ import annotations
import typing as t
import sys
from collections import ChainMap
from dataclasses import fields, Field
from dataclasses import is_dataclass
from .types import MetaData, IteratePropsFunc


def iterate_props(
    typ: t.Type[t.Any], *, ignore_private: bool = True
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], MetaData]]:
    if is_dataclass(typ.__class__):
        typ = typ.__class__

    for field in fields(typ):  # type: Field[t.Any]
        mutable_state: t.Dict[str, t.Any] = {}
        metadata = ChainMap(mutable_state, field.metadata)
        field_type = _evaluate_type(typ, field)
        yield field.name, field_type, metadata


def _evaluate_type(typ: t.Type[t.Any], field: Field[t.Any]) -> t.Type[t.Any]:
    field_type = field.type
    if not isinstance(field_type, str):
        return field_type

    m = sys.modules[typ.__module__]
    # TODO: the types that defined in closure is not supported yet
    field_type = field.type = t._eval_type(
        t.ForwardRef(field_type), m.__dict__, typ.__dict__
    )
    return field_type


# type assertion
_: IteratePropsFunc = iterate_props

__all__ = ["iterate_props", "is_dataclass", "Field", "fields"]
