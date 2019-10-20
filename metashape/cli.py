import typing as t
from metashape.types import T, EmitFunc
from metashape import shortcuts
from metashape.shortcuts import compile  # todo: rename


def run(
    filename: str,
    *,
    aggressive: bool = False,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None,
    emit: t.Optional[EmitFunc] = None,
) -> None:
    from magicalimport import import_module  # type:ignore

    m = import_module(filename)
    if aggressive:
        is_member = (
            lambda x: hasattr(x, "__name__")
            and not hasattr(x, "__loader__")
            and hasattr(x, "__annotations__")
        )  # noqa

    walker = shortcuts.get_walker_from_dict(m.__dict__, is_member=is_member)
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
