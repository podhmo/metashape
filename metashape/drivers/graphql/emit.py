from __future__ import annotations
import typing as t
import logging
import dataclasses
from functools import partial
from metashape.langhelpers import make_dict, reify
from metashape.analyze import ModuleWalker, Member
from metashape.analyze import Context as AnalyzingContext

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


class Context:
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Status:
        has_query: bool = False
        has_mutation: bool = False

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        types: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    def __init__(self, walker: ModuleWalker) -> None:
        self.status = Context.Status()
        self.result = Context.Result()
        self.walker = walker
        self.internal = walker.context

    @reify
    def dumper(self) -> _Dumper:
        return _Dumper()

    status: Context.Status
    result: Context.Result
    walker: ModuleWalker
    internal: AnalyzingContext


class Scanner:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def scan(self, member: Member) -> None:
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        result = self.ctx.result

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
            schema[field_name] = {"type": detect.schema_type(info)}

        result.types[typename] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for m in walker.walk():
            logger.info("walk type: %r", m)
            scanner.scan(m)
    finally:
        ctx.internal.callbacks.teardown()  # xxx:

    ctx.dumper.dump(ctx, output)  # xxx


class _Dumper:
    def dump(self, ctx, o: t.IO[str]) -> None:
        p = partial(print, file=o)
        status = ctx.status
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
        for name, definition in ctx.result.types.items():
            p(f"type {name} {{")
            for fieldname, fieldvalue in definition.items():
                p(f"  {fieldname}: {fieldvalue['type']}")
            p("}")
