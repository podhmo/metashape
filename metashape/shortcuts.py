import typing as t
import sys
import logging
from magicalimport import import_symbol
from .types import EmitFunc, IsMemberFunc
from .marker import is_marked
from .analyze import Member
from .analyze.walker import ModuleWalker
from .analyze.resolver import Resolver


logger = logging.getLogger(__name__)


def get_walker_from_dict(
    d: t.Dict[str, t.Any], *, is_member: t.Optional[IsMemberFunc] = None
) -> ModuleWalker:
    is_member = is_member or is_marked
    members = [v for _, v in sorted(d.items()) if is_member(v)]
    return ModuleWalker(members, resolver=Resolver(is_member=is_member))


def compile_with(
    members: t.List[Member],
    *,
    is_member: t.Optional[IsMemberFunc] = None,
    emit: t.Optional[EmitFunc] = None
) -> None:
    is_member = is_member or is_marked
    w = ModuleWalker(members, resolver=Resolver(is_member=is_member))
    compile(w, emit=emit)


def compile(
    walker: ModuleWalker,
    *,
    output: t.IO = sys.stdout,
    emit: t.Optional[EmitFunc] = None
) -> None:
    emit = emit or import_symbol("metashape.drivers.raw:emit")  # xxx:
    logger.debug("collect members: %d", len(walker))
    emit(walker, output=output)
