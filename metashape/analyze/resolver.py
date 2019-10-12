import typing as t
import typing_extensions as tx
import inspect

from metashape.types import T
from metashape.marker import is_marked
from .core import Member
from .repository import DefaultRepository  # xxx


class Resolver(tx.Protocol):
    def is_member(self, ob: t.Type[T]) -> bool:
        ...

    def resolve_name(self, m: Member) -> str:
        ...

    def resolve_annotations(self, ob: object) -> t.Dict[str, t.Type]:
        ...

    def resolve_description(self, ob: object, *, verbose: bool = False) -> str:
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

    def resolve_annotations(self, ob: object) -> t.Dict[str, t.Type]:
        return t.get_type_hints(ob)

    def resolve_description(self, ob: object, *, verbose: bool = False) -> str:
        doc = inspect.getdoc(ob)
        if doc is None:
            return ""
        if not verbose:
            return doc.split("\n\n", 1)[0]
        return doc

    def resolve_repository(self, d: t.Dict[str, t.Any]) -> "DefaultRepository":
        members = [v for v in d.values() if self.is_member(v)]
        return DefaultRepository(members)
