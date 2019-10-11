import typing as t
import sys
import logging
from metashape.analyze import Accessor


logger = logging.getLogger(__name__)


def compile(accessor: Accessor, *, output: t.IO = sys.stdout) -> None:
    from metashape.flavors.openapi import emit  # TODO: dispatch

    logger.debug("collect members: %d", len(accessor.repository.members))

    emit(accessor, output=output)
