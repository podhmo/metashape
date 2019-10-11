import typing as t
from .analyze.core import Member, Accessor
from .analyze.repository import FakeRepository
from .analyze.resolver import FakeResolver
from .compile import compile


def compile_with(members: t.List[Member]) -> Accessor:
    accessor = Accessor(resolver=FakeResolver(), repository=FakeRepository(members))
    return compile(accessor)
