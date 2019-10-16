import typing as t
from .analyze import Member, Accessor
from .analyze.walker import Walker
from .analyze.resolver import Resolver
from .compile import compile


def compile_with(members: t.List[Member]) -> None:
    accessor = Accessor(
        resolver=Resolver(), walker=Walker(members)
    )
    compile(accessor)
