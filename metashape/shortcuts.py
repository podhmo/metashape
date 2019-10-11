import typing as t
from .analyze.core import Member, Accessor
from .analyze.repository import DefaultRepository
from .analyze.resolver import DefaultResolver
from .compile import compile


def compile_with(members: t.List[Member]) -> Accessor:
    accessor = Accessor(resolver=DefaultResolver(), repository=DefaultRepository(members))
    return compile(accessor)
