from __future__ import annotations
import typing as t
import typing_extensions as tx
import inspect
from types import ModuleType
from metashape.name import resolve_maybe as resolve_name_maybe
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


def get_doc(ob: object, *, verbose: bool = False) -> str:
    doc = inspect.getdoc(ob)
    if doc is None:
        return ""
    if not verbose:
        return doc.split("\n\n", 1)[0]
    return doc


def get_metadata(cls: t.Type[t.Any], name: str) -> t.Optional[MetaData]:
    prop = cls.__dict__.get(name)
    if prop is None:
        return None
    return getattr(prop, "metadata", None)  # type: ignore


def _extract_metadata(
    typ: t.Type[t.Any],
    *,
    metadata: t.Optional[t.Dict[str, t.Any]] = None,
    target_types: t.Collection = (t.Union, tx.Annotated),
    see_args: bool = False,
) -> t.Dict[str, t.Any]:
    if metadata is None:
        metadata = {}

    # for tx.Annotated
    if hasattr(typ, "__metadata__"):
        for x in typ.__metadata__:
            if getattr(x, "see_args", False):
                see_args = True
            if hasattr(x, "as_metadata"):
                metadata.update(x.as_metadata())
            else:
                metadata.update(x.__dict__)
        typ = t.get_args(typ)[0]

    if hasattr(typ, "__origin__") and typ.__origin__:
        if metadata is None:
            metadata = {}
        if see_args or typ.__origin__ in target_types:
            new_args = []
            for x in t.get_args(typ):
                new_arg, _ = _extract_metadata(x, metadata=metadata, see_args=see_args)
                new_args.append(new_arg)
            typ.__args__ = new_args
    return typ, metadata


def iterate_props(
    typ: t.Type[t.Any], *, ignore_private: bool = True, see_annotated: bool = True,
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for fieldname, fieldtype in t.get_type_hints(typ).items():
        if ignore_private and fieldname.startswith("_"):
            continue
        metadata = get_metadata(typ, fieldname)

        # typing_extensions.Annotated?
        if see_annotated:
            fieldtype, metadata = _extract_metadata(fieldtype, metadata=metadata)

        yield fieldname, fieldtype, metadata


# type assertion
_: IteratePropsFunc = iterate_props
