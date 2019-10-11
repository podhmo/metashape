import logging
from metashape.langhelpers import reify
from .core import Member  # noqa
from .repository import Repository
from .resolver import Resolver

logger = logging.getLogger(__name__)


class Context:
    def __init__(self, strict: bool = True):
        self.strict = strict


class Accessor:
    resolver: Resolver
    respository: Repository

    def __init__(self, *, resolver: Resolver, repository: Repository):
        self.resolver = resolver
        self.repository = repository

    @reify
    def context(self) -> Context:
        return Context()
