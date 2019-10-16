import typing as t
import typing_extensions as tx
import inspect

from metashape.types import T
from metashape.marker import is_marked
from . import typeinfo
from .core import Member
from .walker import DefaultWalker  # xxx


class Resolver(tx.Protocol):
    def is_member(self, ob: t.Type[T]) -> bool:
        ...

    def resolve_name(self, m: Member) -> str:
        ...

    def resolve_doc(self, ob: object, *, verbose: bool = False) -> str:
        ...

    def resolve_type_info(self, typ: t.Type[t.Any]) -> typeinfo.TypeInfo:
        ...


class DefaultResolver(Resolver):
    def __init__(
        self, *, is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
    ) -> None:
        self._is_member = is_member or is_marked

    def is_member(self, ob: t.Type[T]) -> bool:
        return self._is_member(ob)

    def resolve_name(self, member: Member) -> str:
        return member.__name__  # type: ignore

    def resolve_doc(self, ob: object, *, verbose: bool = False) -> str:
        return get_doc(ob, verbose=verbose)

    def resolve_type_info(self, typ: t.Type[t.Any]) -> typeinfo.TypeInfo:
        return typeinfo.detect(typ)

    def resolve_walker(self, d: t.Dict[str, t.Any]) -> "DefaultWalker":
        members = [v for _, v in sorted(d.items()) if self.is_member(v)]
        return DefaultWalker(members)


def get_doc(ob: object, *, verbose: bool = False) -> str:
    doc = inspect.getdoc(ob)
    if doc is None:
        return ""
    if not verbose:
        return doc.split("\n\n", 1)[0]
    return doc
