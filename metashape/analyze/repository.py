import typing as t
import typing_extensions as tx
from .core import Member


class Repository(tx.Protocol):
    @property
    def members(self) -> t.List[Member]:  # support also instance variable...
        ...


RepositoryT = t.TypeVar("RepositoryT", bound="Repository")


class DefaultRepository(Repository):
    def __init__(self, members: t.List[t.Any]) -> None:
        self._members = t.cast(t.List[Member], members)  # xxx

    @property
    def members(self) -> t.List[Member]:
        return self._members
