from __future__ import annotations
import typing as t
from collections import deque
from metashape.langhelpers import reify
from metashape.types import T


Store = t.Dict[str, t.Any]


class Context:
    # option parameters
    # state (history)
    # factory of utility objects

    def __init__(self, strict: bool = True, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose

    @reify
    def q(self) -> _Queue:
        return _Queue()

    @reify
    def callbacks(self) -> _Callbacks:
        return _Callbacks()

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


class _Callbacks:
    callbacks = t.List[t.Callable[..., None]]

    def __init__(self):
        self.callbacks = []

    def teardown(self) -> None:
        callbacks, self.callbacks = self.callbacks, []
        for cb in callbacks:
            cb()

    def append(self, cb: t.Callable[..., None]) -> None:
        self.callbacks.append(cb)
