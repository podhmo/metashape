from __future__ import annotations
import typing as t
from collections import deque
import dataclasses
from metashape.langhelpers import reify
from metashape.types import T


Store = t.Dict[str, t.Any]


class Context:
    # option parameters
    # state (history)
    # factory of utility objects
    @dataclasses.dataclass(frozen=False)
    class Option:
        strict: bool = True
        verbose: bool = False
        output_format: str = "json"

    @reify
    def option(self) -> Context.Option:
        return self.__class__.Option()

    @reify
    def q(self) -> _Queue[t.Any]:  # xxx
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
    callbacks: t.List[t.Any]

    def __init__(self) -> None:
        self.callbacks = []  # type: t.List[t.Any]

    def teardown(self) -> None:
        self.callbacks, callbacks = (
            [],
            self.callbacks,
        )  # type: t.List[t.Any], t.List[t.Any]
        for cb in callbacks:
            cb()

    def append(self, cb: t.Callable[..., None]) -> None:
        self.callbacks.append(cb)
