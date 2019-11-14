from __future__ import annotations
import typing as t
import logging
from metashape.marker import guess_mark
from metashape.analyze.walker import ModuleWalker

logger = logging.getLogger(__name__)


def emit(walker: ModuleWalker, *, output: t.Optional[t.IO[str]] = None) -> None:
    output = output or walker.config.option.output
    for m in walker.walk(ignore_private=walker.config.option.ignore_private):
        print(guess_mark(m), m, file=output)
