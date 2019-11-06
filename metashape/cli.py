import typing as t
import sys
import logging
from magicalimport import import_module, import_symbol

from metashape.types import T, EmitFunc
from metashape.runtime import get_walker

logger = logging.getLogger(__name__)


def run(
    filename: str,
    *,
    aggressive: bool = False,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None,
    emit: t.Optional[EmitFunc] = None,
) -> None:
    m = import_module(filename)
    walker = get_walker(m.__dict__, sort=True, aggressive=aggressive, recursive=True)
    emit = emit or import_symbol("metashape.outputs.raw:emit")  # xxx:
    logger.debug("collect members: %d", len(walker))
    emit(walker, output=sys.stdout)


def main(
    *, argv: t.Optional[t.List[str]] = None, emit: t.Optional[EmitFunc] = None
) -> None:
    import argparse
    import logging

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help  # type:ignore
    parser.add_argument("filename")
    parser.add_argument("--aggressive", action="store_true")
    parser.add_argument(
        "--logging", choices=list(logging._nameToLevel.keys()), default="INFO"
    )
    args = parser.parse_args(argv)

    params = vars(args)
    logging.basicConfig(level=params.pop("logging"))
    run(emit=emit, **params)
