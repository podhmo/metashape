from __future__ import annotations
import typing as t
import logging
import dataclasses
import typing_inspect
from metashape.langhelpers import make_dict
from metashape.analyze.walker import Walker
from metashape.analyze.scan import scan as _scan

from . import detect
from ._prestring import Module


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


class Context:
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class State:
        has_query: bool = False
        has_mutation: bool = False

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        types: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)
        enums: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    def __init__(self, walker: Walker) -> None:
        self.state = Context.State()
        self.result = Context.Result()
        self.walker = walker

    state: Context.State
    result: Context.Result
    walker: Walker


def scan(walker: Walker) -> Context:
    ctx = Context(walker)

    resolver = ctx.walker.resolver
    result = ctx.result

    scanned = _scan(walker)

    for enum in scanned.enums:
        result.enums[enum.__name__] = enum
    for cls in scanned.objects:
        schema = make_dict()
        typename = resolver.resolve_typename(cls)
        for field_name, info, metadata in walker.for_type(cls).walk():
            field_name = resolver.metadata.resolve_name(metadata, default=field_name)
            prop = {
                "type": (scanned.get_name(info.normalized) or detect.schema_type(info))
            }
            resolver.metadata.fill_extra_metadata(prop, metadata, name="graphql")
            schema[field_name] = prop

        result.types[typename] = schema
    return ctx


def emit(ctx: Context, *, output: t.IO[str]) -> None:
    m = Module(indent="  ")
    state = ctx.state
    if state.has_query or state.has_query:
        with m.block("schema"):
            if state.has_query:
                m.stmt("query: Query")
            if state.has_mutation:
                m.stmt("mutation: Mutation")

    if state.has_query:
        with m.block("type Query"):
            m.sep()

    for name, definition in ctx.result.enums.items():
        with m.block(f"enum {name}"):
            for x in typing_inspect.get_args(definition):
                m.stmt(x)

    # type
    for name, definition in ctx.result.types.items():
        with m.block(f"type {name}"):
            for fieldname, fieldvalue in definition.items():
                m.stmt(f"{fieldname}: {fieldvalue['type']}")

    print(m, file=output)
