from __future__ import annotations
import typing as t
import logging
from metashape.marker import guess_mark
from metashape.analyze.walker import ModuleWalker

logger = logging.getLogger(__name__)


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    for m in walker.walk(ignore_private=walker.context.option.ignore_private):
        print(guess_mark(m), m, file=output)
