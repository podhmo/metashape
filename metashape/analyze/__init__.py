import logging
from .core import Member  # noqa
from .repository import Repository
from .resolver import Resolver

logger = logging.getLogger(__name__)


class Accessor:
    resolver: Resolver
    respository: Repository

    def __init__(self, *, resolver: Resolver, repository: Repository):
        self.resolver = resolver
        self.repository = repository
