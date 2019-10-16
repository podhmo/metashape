import typing as t
from .types import T
from .marker import is_marked
from .analyze import Member
from .analyze.walker import Walker
from .analyze.resolver import Resolver
from .compile import compile


def get_walker_from_dict(
    d: t.Dict[str, t.Any], *, is_member: t.Optional[t.Callable[[t.Type[T]], bool]]=None
) -> Walker:
    is_member = is_member or is_marked
    members = [v for _, v in sorted(d.items()) if is_member(v)]
    return Walker(members, resolver=Resolver(is_member=is_member))


def compile_with(
    members: t.List[Member],
    *,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
) -> None:
    is_member = is_member or is_marked
    compile(Walker(members, resolver=Resolver(is_member=is_member)))
