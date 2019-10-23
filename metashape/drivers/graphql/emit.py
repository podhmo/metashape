import typing as t
import logging
from functools import partial
from metashape.langhelpers import make_dict
from metashape.analyze import ModuleWalker, Member, Context

# from metashape.analyze import typeinfo
from . import detect

logger = logging.getLogger(__name__)
Store = t.Dict[str, t.Any]

# https://graphql.org/learn/schema/
# https://www.apollographql.com/docs/apollo-server/schema/schema/
#
# TODO: support Array types
# TODO: suport arguments
# TODO: support Query
# TODO: support Mutation
# TODO: support scalar types, perfectly
# TODO: support enumuration types
# TODO: support interfaces
# TODO: support input types
# TODO: support union types


class Scanner:
    def __init__(self, walker: ModuleWalker) -> None:
        self.walker = walker

        self._types = {}

    def scan(self, member: Member, *, store=Store) -> None:
        walker = self.walker
        resolver = self.walker.resolver

        schema = make_dict()
        typename = resolver.resolve_name(member)

        for field_name, field_type, metadata in walker.for_type(member).walk():
            logger.info(
                "walk prop: 	name=%r	type=%r	keys(metadata)=%s",
                field_name,
                field_type,
                (metadata or {}).keys(),
            )
            info = resolver.resolve_type_info(field_type)
            logger.debug("walk prop: 	info=%r", info)
            prop = schema[field_name] = {"type": detect.schema_type(info)}
            if not info["is_optional"]:
                prop["type"] = f"!{prop['type']}"

        self._types[typename] = store["types"][typename] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    store = make_dict(types=make_dict())
    ctx = walker.context
    scanner = Scanner(walker)

    try:
        for m in walker.walk():
            logger.info("walk type: %r", m)
            scanner.scan(m, store=store)
    finally:
        ctx.callbacks.teardown()  # xxx:
    Dumper().dump(store, output)  # xxx


class Dumper:
    def dump(self, store, o: t.IO[str]) -> None:
        p = partial(print, file=o)
        p("schema {")
        p("  query: Query")  # TODO: has query?
        p("  mutation: Mutation")  # TODO: has mutation?
        p("}")
        p("")

        p("type Query {")
        p("}")
        p("")

        for name, definition in store["types"].items():
            p(f"type {name} {{")
            for fieldname, fieldvalue in definition.items():
                p(f"  {fieldname}: {fieldvalue['type']}")
            p("}")
