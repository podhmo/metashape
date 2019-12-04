import typing as t
from dataclasses import fields, Field
from dataclasses import is_dataclass
from .types import MetaData, IteratePropsFunc


def iterate_props(
    typ: t.Type[t.Any], *, ignore_private: bool = True
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for field in fields(typ):  # type: Field[t.Any]
        yield field.name, field.type, field.metadata


# type assertion
_: IteratePropsFunc = iterate_props

__all__ = ["iterate_props", "is_dataclass", "Field", "fields"]
