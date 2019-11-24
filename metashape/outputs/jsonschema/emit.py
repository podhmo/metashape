from __future__ import annotations
import typing as t
import logging
import dataclasses
from dictknife import loading
from metashape.types import Member, _ForwardRef
from metashape.langhelpers import make_dict
from metashape.analyze import typeinfo
from metashape.analyze.walker import ModuleWalker
from metashape.analyze.config import Config as AnalyzingConfig
from . import detect

logger = logging.getLogger(__name__)

# TODO: some validations
# TODO: additionalProperties
# TODO: conflict name
# TODO: type defined by array
# TODO: toplevel definitions
# TODO: drop discriminator


class Context:  # TODO: rename to context?
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class State:
        schemas: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        result: t.Dict[str, t.Any] = dataclasses.field(
            default_factory=lambda: make_dict(definitions=make_dict())
        )

    def __init__(self, walker: ModuleWalker) -> None:
        self.state = Context.State()
        self.result = Context.Result()
        self.walker = walker
        self.config = walker.config

    state: Context.State
    result: Context.Result
    walker: ModuleWalker
    config: AnalyzingConfig


class Scanner:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def _build_ref_data(
        self, field_type: t.Union[t.Type[t.Any], _ForwardRef]
    ) -> t.Dict[str, t.Any]:
        resolver = self.ctx.walker.resolver
        return {
            "$ref": f"#/definitions/{resolver.resolve_typename(field_type)}"
        }  # todo: lazy

    def _build_one_of_data(self, info: typeinfo.TypeInfo) -> t.Dict[str, t.Any]:
        candidates: t.List[t.Dict[str, t.Any]] = []

        for x in typeinfo.get_args(info):
            custom = typeinfo.get_custom(x)
            if custom is None:
                candidates.append({"type": detect.schema_type(x)})
            else:
                candidates.append(self._build_ref_data(custom))
        prop = {"oneOf": candidates}  # todo: discriminator
        return prop

    def scan(self, cls: Member) -> None:
        ctx = self.ctx
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        cfg = self.ctx.config

        typename = resolver.resolve_typename(cls)

        required: t.List[str] = []
        properties: t.Dict[str, t.Any] = make_dict()
        description = resolver.metadata.resolve_doc(cls, verbose=cfg.option.verbose)

        schema: t.Dict[str, t.Any] = make_dict(
            properties=properties, required=required, description=description
        )

        for field_name, info, metadata in walker.for_type(cls).walk(
            ignore_private=cfg.option.ignore_private
        ):
            if not info.is_optional:
                required.append(field_name)

            # TODO: self recursion check (warning)
            if resolver.is_member(info.normalized):
                walker.append(info.normalized)

                properties[field_name] = self._build_ref_data(info.normalized)
                continue

            if typeinfo.is_composite(info):
                properties[field_name] = prop = self._build_one_of_data(info)
            else:
                prop = properties[field_name] = {"type": detect.schema_type(info)}
                enum = detect.enum(info)
                if enum:
                    prop["enum"] = enum

            # default
            if resolver.metadata.has_default(metadata):
                prop["default"] = resolver.metadata.resolve_default(metadata)
            resolver.metadata.fill_extra_metadata(prop, metadata, name="jsonschema")

            if prop.get("type") == "array":  # todo: simplify with recursion
                assert len(typeinfo.get_args(info)) == 1
                first = typeinfo.get_args(info)[0]
                if typeinfo.is_composite(first):
                    prop["items"] = self._build_one_of_data(first)
                else:
                    custom = typeinfo.get_custom(first)
                    if custom is None:
                        prop["items"] = detect.schema_type(first)
                    else:
                        custom_type = custom
                        prop["items"] = self._build_ref_data(custom_type)

        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        if cfg.option.strict and "additionalProperties" not in schema:
            schema["additionalProperties"] = False

        ctx.state.schemas[typename] = ctx.result.result["definitions"][
            typename
        ] = schema


def scan(walker: ModuleWalker, *, definitions: t.Optional[str] = None) -> Context:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for i, m in enumerate(
            walker.walk(ignore_private=ctx.config.option.ignore_private)
        ):
            scanner.scan(m)
            if i == 0 and definitions is None:
                scanner.ctx.result.result[
                    "$ref"
                ] = f"#/definitions/{walker.resolver.resolve_typename(m)}"

    finally:
        ctx.config.callbacks.teardown()  # xxx:
    return ctx


def emit(ctx: Context, *, output: t.IO[str]) -> None:
    loading.dump(ctx.result.result, output, format=ctx.config.option.output_format)
