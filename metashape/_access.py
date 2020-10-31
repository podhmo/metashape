from __future__ import annotations
import typing as t
import typing_extensions as tx
import sys
import inspect
from types import ModuleType
from metashape.name import resolve_maybe as resolve_name_maybe
from metashape.langhelpers import typing_get_args
from .types import MetaData, Member, _ForwardRef
from .types import IteratePropsFunc


class SeeArgsForMetadata:
    see_args: bool = True


def get_name(member: t.Union[ModuleType, Member, _ForwardRef]) -> str:
    name_ = resolve_name_maybe(member)  # type: ignore
    if name_ is not None:
        return name_
    # for ForwardRef
    name = getattr(member, "__forward_arg__", None)  # type: t.Optional[str]
    if name is not None:
        return name
    return member.__class__.__name__


def get_fullname(member: t.Union[ModuleType, Member, _ForwardRef]) -> str:
    if hasattr(member, "__file__"):  # module type
        return member.__name__  # type: ignore
    if hasattr(member, "__module__"):
        return f"{member.__module__}.{get_name(member)}"
    else:
        return f"?.{get_name(member)}"


def get_doc(ob: object, *, verbose: bool = False) -> str:
    doc = inspect.getdoc(ob)
    if doc is None:
        return ""
    if not verbose:
        return doc.split("\n\n", 1)[0]
    return doc


def get_metadata(cls: t.Type[t.Any], name: str) -> MetaData:
    prop = cls.__dict__.get(name)
    if prop is None:
        return {}
    return getattr(prop, "metadata", None) or {}


def _extract_metadata(
    typ: t.Type[t.Any],
    *,
    metadata: t.Optional[t.Dict[str, t.Any]] = None,
    target_types: t.List[object] = [t.Union, tx.Annotated],
    see_args: bool = False,
) -> t.Tuple[t.Type[t.Any], t.Dict[str, t.Any]]:
    if metadata is None:
        metadata = {}

    # for tx.Annotated
    if hasattr(typ, "__metadata__"):
        for x in typ.__metadata__:
            if getattr(x, "see_args", False):
                see_args = True
            if hasattr(x, "as_metadata"):
                metadata.update(x.as_metadata())
            elif hasattr(x, "__slots__"):
                for name in x.__slots__:
                    metadata[name] = getattr(x, name)
            else:
                metadata.update(x.__dict__)
        typ = typing_get_args(typ)[0]

    if hasattr(typ, "__origin__") and typ.__origin__:
        if metadata is None:
            metadata = {}
        if see_args or typ.__origin__ in target_types:
            new_args = []
            for x in typing_get_args(typ):
                new_arg, _ = _extract_metadata(x, metadata=metadata, see_args=see_args)
                new_args.append(new_arg)
            typ.__args__ = new_args
    return typ, metadata


if sys.version_info >= (3, 9):
    from functools import partial

    _get_type_hints = partial(t.get_type_hints, include_extras=True)
else:
    _get_type_hints = t.get_type_hints


def iterate_props(
    typ: t.Type[t.Any], *, ignore_private: bool = True,
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], MetaData]]:
    see_annotated: bool = True
    hints = _get_type_hints(typ, localns=getattr(typ, "__dict__", None))
    for fieldname, fieldtype in hints.items():
        if ignore_private and fieldname.startswith("_"):
            continue
        metadata = get_metadata(typ, fieldname)

        # typing_extensions.Annotated?
        if see_annotated:
            fieldtype, metadata = _extract_metadata(fieldtype, metadata=metadata)  # type: ignore

        yield fieldname, fieldtype, metadata


# type assertion
_: IteratePropsFunc = iterate_props
