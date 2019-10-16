import typing as t
import sys
import logging
from magicalimport import import_symbol
from .types import T
from .marker import is_marked
from .analyze import Member
from .analyze.walker import Walker
from .analyze.resolver import Resolver


logger = logging.getLogger(__name__)


def get_walker_from_dict(
    d: t.Dict[str, t.Any],
    *,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
) -> Walker:
    is_member = is_member or is_marked
    members = [v for _, v in sorted(d.items()) if is_member(v)]
    return Walker(members, resolver=Resolver(is_member=is_member))


def compile_with(
    members: t.List[Member],
    *,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None,
    emit: t.Optional[callable] = None  # todo: emit's type
) -> None:
    is_member = is_member or is_marked
    w = Walker(members, resolver=Resolver(is_member=is_member))
    compile(w, emit=emit)


def compile(
    walker: Walker,
    *,
    output: t.IO = sys.stdout,
    emit: t.Optional[callable] = None  # todo: emit's type
) -> None:
    emit = emit or import_symbol("metashape.drivers.openapi:emit")
    logger.debug("collect members: %d", len(walker.walk_module()))
    emit(walker, output=output)
