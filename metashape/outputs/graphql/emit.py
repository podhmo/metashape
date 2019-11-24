from __future__ import annotations
import typing as t
import logging
import dataclasses
from functools import partial
import typing_inspect
from metashape.langhelpers import make_dict
from metashape.analyze.walker import Walker, Walked
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


class Context:
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class State:
        has_query: bool = False
        has_mutation: bool = False
        walked: Walked = None  # todo: remove

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        types: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    def __init__(self, walker: Walker, *, walked: Walked) -> None:
        self.state = Context.State(walked=walked)
        self.result = Context.Result()
        self.walker = walker
        self.config = walker.config

    state: Context.State
    result: Context.Result
    walker: Walker
    config: AnalyzingConfig


def scan(walker: Walker) -> Context:
    walked = walker.walked(kinds=["object", "enum"])
    ctx = Context(walker, walked=walked)

    resolver = ctx.walker.resolver
    result = ctx.result

    try:
        for cls in walked.objects:
            schema = make_dict()
            typename = resolver.resolve_typename(cls)
            for field_name, info, metadata in walker.for_type(cls).walk():
                prop = {
                    "type": (
                        walked.get_name(info.normalized) or detect.schema_type(info)
                    )
                }
                resolver.metadata.fill_extra_metadata(prop, metadata, name="graphql")
                schema[field_name] = prop

            result.types[typename] = schema
    finally:
        ctx.config.callbacks.teardown()  # xxx:
    return ctx


def emit(ctx: Context, *, output: t.IO[str]) -> None:
    p = partial(print, file=output)
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

    for definition in ctx.state.walked.enums:
        p(f"enum {definition.__name__} {{")
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
