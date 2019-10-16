import typing as t
from .analyze import Member, Accessor
from .analyze.walker import DefaultWalker
from .analyze.resolver import DefaultResolver
from .compile import compile


def compile_with(members: t.List[Member]) -> None:
    accessor = Accessor(
        resolver=DefaultResolver(), walker=DefaultWalker(members)
    )
    compile(accessor)
