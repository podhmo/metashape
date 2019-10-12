import typing as t
import logging
from collections import deque
from metashape.langhelpers import reify
from .core import Member  # noqa
from .repository import Repository
from .resolver import Resolver

logger = logging.getLogger(__name__)


class Context:
    def __init__(self, strict: bool = True, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose


class Accessor:
    resolver: Resolver
    respository: Repository

    def __init__(self, *, resolver: Resolver, repository: Repository):
        self.resolver = resolver
        self.repository = repository

    @reify
    def context(self) -> Context:
        return Context()

    @reify
    def q(self) -> "_Queue":
        return _Queue()


class _Queue:
    q: t.Deque[Member]
    seen: t.Set[Member]

    def __init__(self) -> None:
        self.q = deque()
        self.seen = set()

    def append(self, x: Member) -> None:
        self.q.append(x)

    def popleft(self) -> Member:  # raise IndexError
        while True:
            x = self.q.popleft()
            if x in self.seen:
                continue
            self.seen.add(x)
            return x
