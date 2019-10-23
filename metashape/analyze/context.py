from __future__ import annotations
import typing as t
from collections import deque
from metashape.langhelpers import reify
from metashape.types import T


Store = t.Dict[str, t.Any]


class Context:
    def __init__(self, strict: bool = True, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose

    @reify
    def q(self) -> _Queue:
        return _Queue()

    @reify
    def dumper(self) -> t.Any:  # type: ignore
        from dictknife import loading

        return loading


class _Queue(t.Generic[T]):
    q: t.Deque[T]
    seen: t.Set[T]

    def __init__(self) -> None:
        self.q = deque()
        self.seen = set()

    def append(self, x: T) -> None:
        self.q.append(x)

    def popleft(self) -> T:  # raise IndexError
        while True:
            x = self.q.popleft()
            if x in self.seen:
                continue
            self.seen.add(x)
            return x
