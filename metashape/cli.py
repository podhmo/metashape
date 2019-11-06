import typing as t
from magicalimport import import_module

from metashape.types import T, EmitFunc
from metashape.shortcuts import compile  # todo: rename
from metashape.runtime import get_walker


def run(
    filename: str,
    *,
    aggressive: bool = False,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None,
    emit: t.Optional[EmitFunc] = None,
) -> None:
    m = import_module(filename)
    walker = get_walker(m.__dict__, sort=True, aggressive=aggressive, recursive=True)
    compile(walker, emit=emit)


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
