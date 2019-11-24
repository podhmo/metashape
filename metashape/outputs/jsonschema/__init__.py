import typing as t
from metashape.analyze.walker import Walker
from .emit import emit, scan


def codegen(walker: Walker, *, output: t.Optional[t.IO[str]] = None) -> None:
    output = output or walker.config.option.output
    ctx = scan(walker)
    emit(ctx, output=output)
