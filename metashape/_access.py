import typing as t
import inspect
from .types import MetaData, Member, _ForwardRef


def get_name(member: t.Union[Member, _ForwardRef]) -> str:
    name = getattr(member, "__name__", None)  # type: t.Optional[str]
    if name is not None:
        return name
    # for ForwardRef
    return member.__forward_arg__


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


def iterate_props(
    typ: t.Type[t.Any], *, ignore_private: bool = True
) -> t.Iterable[t.Tuple[str, t.Type[t.Any], t.Optional[MetaData]]]:
    for fieldname, fieldtype in t.get_type_hints(typ).items():
        if ignore_private and fieldname.startswith("_"):
            continue
        yield fieldname, fieldtype, get_metadata(typ, fieldname)
