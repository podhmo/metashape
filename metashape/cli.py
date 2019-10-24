import typing as t
import typing_extensions as tx
from metashape.types import T, EmitFunc, Kind
from metashape import shortcuts
from metashape.marker import mark
from metashape.shortcuts import compile  # todo: rename


def guess_kind_aggressive(x: t.Type) -> t.Optional[Kind]:
    # is custom class?
    if hasattr(x, "__name__"):
        if not hasattr(x, "__loader__") and hasattr(x, "__annotations__"):
            return object
        else:
            return None

    # is tx.Literal?
    if hasattr(x, "__origin__") and x.__origin__ is tx.Literal:
        return tx.Literal

    return None


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
        for name, v in list(m.__dict__.items()):
            kind = guess_kind_aggressive(v)
            if kind is not None:
                if kind == "enum":
                    v.__name__ = name  # xxx TODO: use tx.Annotated
                mark(v, kind=kind)
    walker = shortcuts.get_walker_from_dict(m.__dict__)
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
