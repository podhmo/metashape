import typing as t
import typing_extensions as tx

from metashape.types import T
from metashape.marker import is_marked
from .core import Member
from .repository import FakeRepository  # xxx


class Resolver(tx.Protocol):
    def is_member(self, ob: t.Type[T]) -> bool:
        ...

    def resolve_name(self, m: Member) -> str:
        ...

    def resolve_annotations(self, ob: object) -> t.Dict[str, t.Type]:
        ...


class FakeResolver(Resolver):
    def __init__(
        self, *, is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
    ) -> None:
        self._is_member = is_member or is_marked

    def is_member(self, ob: t.Type[T]) -> bool:
        return self._is_member(ob)

    def resolve_name(self, member: Member) -> str:
        return member.__name__  # type: ignore

    def resolve_annotations(self, ob: object) -> t.Dict[str, t.Type]:
        return ob.__annotations__

    def resolve_repository(self, d: t.Dict[str, t.Any]) -> "FakeRepository":
        members = [v for v in d.values() if self.is_member(v)]
        return FakeRepository(members)
