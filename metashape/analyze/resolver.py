import typing as t
import inspect

from metashape.types import T, Member, _ForwardRef
from metashape.marker import is_marked
from . import typeinfo


class Resolver:
    def __init__(
        self, *, is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
    ) -> None:
        self._is_member = is_member or is_marked

    def is_member(self, ob: t.Type[T]) -> bool:
        return self._is_member(ob)

    def resolve_name(self, member: t.Union[Member, _ForwardRef]) -> str:
        name = getattr(member, "__name__", None)  # type: t.Optional[str]
        if name is not None:
            return name
        # for ForwardRef
        return member.__forward_arg__

    def resolve_doc(self, ob: object, *, verbose: bool = False) -> str:
        return get_doc(ob, verbose=verbose)

    def resolve_type_info(self, typ: t.Type[t.Any]) -> typeinfo.TypeInfo:
        return typeinfo.typeinfo(typ)


def get_doc(ob: object, *, verbose: bool = False) -> str:
    doc = inspect.getdoc(ob)
    if doc is None:
        return ""
    if not verbose:
        return doc.split("\n\n", 1)[0]
    return doc
