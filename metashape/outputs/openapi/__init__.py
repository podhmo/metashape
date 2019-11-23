from metashape.analyze.walker import ModuleWalker
import typing as t
from .emit import emit, scan


def codegen(walker: ModuleWalker, *, output: t.Optional[t.IO[str]] = None) -> None:
    output = output or walker.config.option.output
    ctx = scan(walker)
    emit(ctx, output=output)
