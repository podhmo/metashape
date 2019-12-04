from __future__ import annotations
import typing as t
import logging
import dataclasses
from functools import partial
import typing_inspect
from metashape.types import Member
from metashape.marker import guess_mark
from metashape.langhelpers import make_dict, reify
from metashape.analyze.typeinfo import TypeInfo
from metashape.analyze.walker import Walker
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
    def __init__(self, enum_type_to_name: t.Dict[t.Type[t.Any], str], info: TypeInfo):
        self.enum_type_to_name = enum_type_to_name
        self.info = info

    def __str__(self) -> str:
        typ = self.info.normalized
        return self.enum_type_to_name.get(typ) or detect.schema_type(self.info)


class Context:
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class State:
        has_query: bool = False
        has_mutation: bool = False
        enum_type_to_name: t.Dict[t.Any, str] = dataclasses.field(
            default_factory=make_dict
        )

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        types: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    def __init__(self, walker: Walker) -> None:
        self.state = Context.State()
        self.result = Context.Result()
        self.walker = walker
        self.config = walker.config

    @reify
    def dumper(self) -> _Dumper:
        return _Dumper()

    state: Context.State
    result: Context.Result
    walker: Walker
    config: AnalyzingConfig


class Scanner:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def scan(self, cls: Member) -> None:
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        result = self.ctx.result
        state = self.ctx.state

        schema = make_dict()
        typename = resolver.resolve_typename(cls)

        for field_name, info, metadata in walker.for_type(cls).walk():
            field_name = resolver.metadata.resolve_name(metadata, default=field_name)

            prop = {"type": _LazyType(state.enum_type_to_name, info)}
            resolver.metadata.fill_extra_metadata(prop, metadata, name="graphql")
            schema[field_name] = prop

        result.types[typename] = schema


def scan(walker: Walker) -> Context:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for cls in walker.walk(kinds=["object", "enum"]):
            if guess_mark(cls) == "enum":
                ctx.state.enum_type_to_name[cls] = cls.__name__
            else:
                scanner.scan(cls)
    finally:
        ctx.config.callbacks.teardown()  # xxx:
    return ctx


def emit(ctx: Context, *, output: t.IO[str]) -> None:
    ctx.dumper.dump(ctx, output)  # xxx


class _Dumper:
    def dump(self, ctx: Context, o: t.IO[str]) -> None:
        p = partial(print, file=o)
        state = ctx.state
        if state.has_query or state.has_query:
            p("schema {")
            if state.has_query:
                p("  query: Query")
            if state.has_mutation:
                p("  mutation: Mutation")
            p("}")
            p("")

        if state.has_query:
            p("type Query {")
            p("}")
            p("")

        # enum (todo: rename attributes)
        for definition, name in ctx.state.enum_type_to_name.items():
            p(f"enum {name} {{")
            for x in typing_inspect.get_args(definition):
                p(f"  {x}")
            p("}")
            p("")

        # type
        for name, definition in ctx.result.types.items():
            p(f"type {name} {{")
            for fieldname, fieldvalue in definition.items():
                p(f"  {fieldname}: {fieldvalue['type']}")
            p("}")
