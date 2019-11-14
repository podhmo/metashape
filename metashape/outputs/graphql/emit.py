from __future__ import annotations
import typing as t
import logging
import dataclasses
from functools import partial
import typing_inspect
from metashape.types import Member
from metashape.marker import guess_mark
from metashape.langhelpers import make_dict, reify
from metashape.analyze import typeinfo
from metashape.analyze.walker import ModuleWalker
from metashape.analyze.config import Config as AnalyzingConfig

from . import detect

logger = logging.getLogger(__name__)

# https://graphql.org/learn/schema/
# https://www.apollographql.com/docs/apollo-server/schema/schema/
#
# TODO: comments
# TODO: suport arguments
# TODO: support Query
# TODO: support Mutation
# TODO: support interfaces
# TODO: support input types
# TODO: support union types
# TODO: support new scalar types


class _LazyType:
    def __init__(
        self, enum_type_to_name: t.Dict[t.Type[t.Any], str], info: typeinfo.TypeInfo
    ):
        self.enum_type_to_name = enum_type_to_name
        self.info = info

    def __str__(self) -> str:
        typ = self.info.normalized
        return self.enum_type_to_name.get(typ) or detect.schema_type(self.info)


class Context:
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Status:
        has_query: bool = False
        has_mutation: bool = False

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        enum_type_to_name: t.Dict[t.Any, str] = dataclasses.field(
            default_factory=make_dict
        )
        name_to_type: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    def __init__(self, walker: ModuleWalker) -> None:
        self.status = Context.Status()
        self.result = Context.Result()
        self.walker = walker
        self.config = walker.config

    @reify
    def dumper(self) -> _Dumper:
        return _Dumper()

    status: Context.Status
    result: Context.Result
    walker: ModuleWalker
    config: AnalyzingConfig


class Scanner:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def scan(self, member: Member) -> None:
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        result = self.ctx.result
        cfg = self.ctx.config

        schema = make_dict()
        typename = resolver.resolve_typename(member)

        for field_name, info, metadata in walker.for_type(member).walk(
            ignore_private=cfg.option.ignore_private
        ):
            schema[field_name] = {"type": _LazyType(result.enum_type_to_name, info)}

        result.name_to_type[typename] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for m in walker.walk(kinds=["object", "enum"]):
            logger.info("walk type: %r", m)
            if guess_mark(m) == "enum":
                ctx.result.enum_type_to_name[m] = m.__name__
            else:
                scanner.scan(m)
    finally:
        ctx.config.callbacks.teardown()  # xxx:

    ctx.dumper.dump(ctx, output)  # xxx


class _Dumper:
    def dump(self, ctx: Context, o: t.IO[str]) -> None:
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

        # enum
        for definition, name in ctx.result.enum_type_to_name.items():
            p(f"enum {name} {{")
            for x in typing_inspect.get_args(definition):
                p(f"  {x}")
            p("}")
            p("")

        # type
        for name, definition in ctx.result.name_to_type.items():
            p(f"type {name} {{")
            for fieldname, fieldvalue in definition.items():
                p(f"  {fieldname}: {fieldvalue['type']}")
            p("}")
