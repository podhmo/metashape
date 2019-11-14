from __future__ import annotations
import typing as t
import sys
from collections import deque
import dataclasses
from metashape.langhelpers import reify
from metashape.types import T, Member


Store = t.Dict[str, t.Any]


class Context:
    # option parameters
    # state (history)
    # factory of utility objects
    @dataclasses.dataclass(frozen=False)
    class Option:
        strict: bool = True
        verbose: bool = False
        ignore_private: bool = True
        output_format: str = "json"
        recursive: bool = False
        sort: bool = True  # default false?
        output: t.IO[str] = sys.stdout  # xxx:

    def __init__(self, option: t.Optional[Context.Option] = None):
        self.option = option or self.__class__.Option()

    @reify
    def q(self) -> _Queue[Member]:
        return _Queue()

    @reify
    def callbacks(self) -> _Callbacks:
        return _Callbacks()


class _Queue(t.Generic[T]):
    q: t.Deque[T]
    seen: t.Set[T]

    def __init__(self) -> None:
        self.q = deque()
        self.seen = set()

    def __contains__(self, x: T) -> bool:
        return x in self.seen

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
    callbacks: t.List[t.Callable[..., None]]

    def __init__(self) -> None:
        self.callbacks = []

    def teardown(self) -> None:
        self.callbacks, callbacks = [], self.callbacks
        for cb in callbacks:
            cb()

    def append(self, cb: t.Callable[..., None]) -> None:
        self.callbacks.append(cb)
