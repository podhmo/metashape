import typing as t
import logging
import dataclasses
from functools import partial
from metashape.langhelpers import make_dict
from metashape.analyze import ModuleWalker, Member

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


class _State:  # TODO: rename to context?
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Status:
        has_query: bool = False
        has_mutation: bool = False

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        types: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    def __init__(self) -> None:
        self.status = _State.Status()
        self.result = _State.Result()


class Scanner:
    def __init__(self, walker: ModuleWalker) -> None:
        self.walker = walker

    def scan(self, member: Member, *, state: _State) -> None:
        walker = self.walker
        resolver = self.walker.resolver
        result = state.result

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

        result.types[typename] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    ctx = walker.context
    state = _State()
    scanner = Scanner(walker)

    try:
        for m in walker.walk():
            logger.info("walk type: %r", m)
            scanner.scan(m, state=state)
    finally:
        ctx.callbacks.teardown()  # xxx:
    Emiter().emit(state, output)  # xxx


class Emiter:
    def emit(self, state, o: t.IO[str]) -> None:
        p = partial(print, file=o)
        status = state.status
        if status.has_query or status.has_query:
            p("schema {")
            if status.has_query:
                p("  query: Query")
            if status.has_mutation:
                p("  mutation: Mutation")
            p("}")
            p("")

        if status.has_query:
            p("type Query {")
            p("}")
            p("")

        # types
        for name, definition in state.result.types.items():
            p(f"type {name} {{")
            for fieldname, fieldvalue in definition.items():
                p(f"  {fieldname}: {fieldvalue['type']}")
            p("}")
