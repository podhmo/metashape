import typing as t
import sys
import logging
from magicalimport import import_symbol
from .types import EmitFunc, IsMemberFunc, Member
from .marker import is_marked
from .analyze.walker import ModuleWalker
from .analyze.resolver import Resolver

# TODO: remove this module?

logger = logging.getLogger(__name__)


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
    output: t.IO[str] = sys.stdout,
    emit: t.Optional[EmitFunc] = None
) -> None:
    emit = emit or import_symbol("metashape.outputs.raw:emit")  # xxx:
    logger.debug("collect members: %d", len(walker))
    emit(walker, output=output)
