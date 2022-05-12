from metashape.analyze.walker import Walker
import typing as t
from .emit import emit, scan


def codegen(walker: Walker, *, output: t.Optional[t.IO[str]] = None, hooks: t.Optional[t.List[str]]=None) -> None:
    output = output or walker.config.option.output
    ctx = scan(walker)
    emit(ctx, output=output, hooks=hooks)
