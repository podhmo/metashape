import typing as t
from collections import defaultdict
import dataclasses
from metashape.types import Kind, Member
from metashape.marker import guess_mark
from .walker import Walker


@dataclasses.dataclass(frozen=True)
class Scanned:
    seen: t.Dict[Kind, t.List[Member]]
    names: t.Dict[Member, str]
    _history: t.List[Member]

    def __iter__(self) -> t.Iterable[Member]:
        return iter(self._history)

    @property
    def enums(self) -> t.List[Member]:
        return self.seen["enum"]

    @property
    def objects(self) -> t.List[Member]:
        return self.seen["object"]

    def get_name(self, m: Member) -> t.Optional[str]:
        return self.names.get(m)


def scan(
    w: Walker, *, kinds: t.List[Kind] = ["object", "enum"], ignore_private: bool = False
) -> Scanned:
    seen: t.Dict[Kind, t.List[Member]] = defaultdict(list)
    names: t.Dict[Member, str] = {}
    history: t.List[Member] = []
    resolver = w.resolver

    for m in w.walk(kinds=kinds, ignore_private=ignore_private):
        kind = guess_mark(m)
        names[m] = resolver.resolve_typename(m)
        seen[kind].append(m)  # type: ignore
        history.append(m)
    return Scanned(seen=seen, names=names, _history=history)
