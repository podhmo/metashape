import typing as t
import sys
import logging
from metashape.analyze.walker import Walker


logger = logging.getLogger(__name__)


def compile(walker: Walker, *, output: t.IO = sys.stdout) -> None:
    from metashape.flavors.openapi import emit  # TODO: dispatch

    logger.debug("collect members: %d", len(walker.walk_module()))

    emit(walker, output=output)
