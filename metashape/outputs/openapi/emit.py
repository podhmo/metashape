from __future__ import annotations
import typing as t
import typing_extensions as tx
import logging
import dataclasses
from functools import partial
from dictknife import loading
from metashape.types import Member
from metashape.langhelpers import make_dict, reify
from metashape.typeinfo import TypeInfo
from metashape.analyze.resolver import Resolver
from metashape.analyze.walker import Walker
from metashape.analyze.config import Config as AnalyzingConfig

from . import detect

logger = logging.getLogger(__name__)

# TODO: some validations
# TODO: additionalProperties
# TODO: conflict name


class Context:
    state: Context.State
    result: ResultDict
    resolver: Resolver
    config: AnalyzingConfig

    def __init__(self, walker: Walker) -> None:
        self.state = Context.State()
        self.result = {"components": {"schemas": {}}}
        self.resolver = walker.resolver
        self.config = walker.config

    @property
    def verbose(self) -> bool:
        return self.config.option.verbose

    @property
    def strict(self) -> bool:
        return self.config.option.strict

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class State:
        schemas: t.Dict[str, SchemaDict] = dataclasses.field(default_factory=make_dict)
        refs: t.Dict[t.Type[t.Any], t.Dict[str, str]] = dataclasses.field(
            default_factory=make_dict
        )

    def register_schema(self, cls: t.Type[t.Any], schema: SchemaDict) -> None:
        typename = self.resolver.resolve_typename(cls)
        self.state.schemas[typename] = self.result["components"]["schemas"][
            typename
        ] = schema
        self.state.refs[cls] = {"$ref": f"#/components/schemas/{typename}"}


class ResultDict(tx.TypedDict):
    components: ComponentDict


class ComponentDict(tx.TypedDict):
    schemas: t.Dict[str, SchemaDict]


class SchemaDict(tx.TypedDict, total=False):
    type: detect.JSONSchemaType

    description: str
    properties: t.Any
    required: t.List[str]
    additionalProperties: t.Union[bool, t.Dict[str, t.Any]]


class _Fixer:
    ctx: Context

    def __init__(self, ctx: Context, *, discriminator_name: str) -> None:
        self.ctx = ctx
        self.discriminator_name = discriminator_name

    def register_fix_discriminator_callback(self, info: TypeInfo) -> None:
        resolver = self.ctx.resolver

        for x in info.args:
            if x.user_defined_type is None:
                continue
            name = resolver.resolve_typename(x.user_defined_type)
            self.ctx.config.callbacks.append(
                partial(self.fix_discriminator, name, fieldname=self.discriminator_name)
            )

    def fix_discriminator(self, name: str, *, fieldname: str) -> None:
        state = self.ctx.state
        schema = state.schemas.get(name)
        if schema is None:
            return
        props = schema.get("properties")
        if props is None:
            return
        if fieldname in props:
            return
        props[fieldname] = {"type": "string"}  # xxx
        if "required" in schema:
            schema["required"].append(fieldname)
        else:
            schema["required"] = [fieldname]


class Scanner:
    DISCRIMINATOR_FIELD = "$type"

    def __init__(self, ctx: Context, *, walker: Walker) -> None:
        self.ctx = ctx
        self.walker = walker

    @reify
    def fixer(self) -> _Fixer:
        return _Fixer(self.ctx, discriminator_name=self.DISCRIMINATOR_FIELD)

    def _build_ref_data(self, field_type: Member) -> t.Dict[str, t.Any]:
        resolver = self.ctx.resolver
        self.walker.append(field_type)
        return {
            "$ref": f"#/components/schemas/{resolver.resolve_typename(field_type)}"
        }  # todo: lazy

    def _build_one_of_data(self, info: TypeInfo) -> t.Dict[str, t.Any]:
        candidates: t.List[t.Dict[str, t.Any]] = []
        need_discriminator = True

        for x in info.args:
            if x.user_defined_type is None:
                need_discriminator = False
                candidates.append({"type": detect.schema_type(x)})
            else:
                candidates.append(self._build_ref_data(x.user_defined_type))

        prop: t.Dict[str, t.Any] = {"oneOf": candidates}
        if need_discriminator:
            prop["discriminator"] = {"propertyName": self.DISCRIMINATOR_FIELD}
            self.fixer.register_fix_discriminator_callback(info)

        return prop

    def scan(self, cls: Member) -> None:
        ctx = self.ctx
        walker = self.walker
        resolver = self.ctx.resolver
        metadata_resolver = resolver.metadata

        required: t.List[str] = []
        properties: t.Dict[str, t.Any] = make_dict()
        description: str = metadata_resolver.resolve_doc(cls, verbose=ctx.verbose)

        schema: SchemaDict = make_dict(
            type="object",
            properties=properties,
            required=required,
            description=description,
        )

        for field_name, info, metadata in walker.walk_fields(cls):
            field_name = metadata_resolver.resolve_name(metadata, default=field_name)
            if not info.is_optional:
                required.append(field_name)

            # TODO: self recursion check (warning)
            if resolver.is_member(info.type_) and resolver.resolve_typename(info.type_):
                properties[field_name] = self._build_ref_data(info.type_)
                continue

            if info.is_combined:
                properties[field_name] = prop = self._build_one_of_data(info)
            else:
                prop = properties[field_name] = {"type": detect.schema_type(info)}
                enum = detect.enum(info)
                if enum:
                    prop["enum"] = enum

            # description
            if metadata.get("description"):
                prop["description"] = metadata_resolver.resolve_doc(
                    info.type_, verbose=True, value=metadata["description"]
                )

            # default
            if metadata_resolver.has_default(metadata):
                prop["default"] = metadata_resolver.resolve_default(metadata)
            metadata_resolver.fill_extra_metadata(prop, metadata, name="openapi")

            if prop.get("type") == "array":  # todo: simplify with recursion
                assert len(info.args) == 1
                first = info.args[0]
                if first.is_combined and first.is_container:
                    prop["items"] = self._build_one_of_data(first)
                elif first.user_defined_type is None:
                    prop["items"] = detect.schema_type(first)
                else:
                    if first.user_defined_type is not None:
                        prop["items"] = self._build_ref_data(first.user_defined_type)

            if info.is_newtype:
                if info.user_defined_type is not None:
                    if prop.get("type") == "object":
                        prop.pop("type")
                        prop.update(ctx.state.refs[info.user_defined_type])
                else:
                    if hasattr(info.supertypes[0], "__name__"):
                        prop["format"] = resolver.resolve_typeformat(info)

        # simplify
        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        if ctx.strict and "additionalProperties" not in schema:
            schema["additionalProperties"] = False

        ctx.register_schema(cls, schema)


def scan(walker: Walker,) -> Context:
    ctx = Context(walker)
    scanner = Scanner(ctx, walker=walker)

    try:
        for cls in walker.walk():
            scanner.scan(cls)
    finally:
        ctx.config.callbacks.teardown()  # xxx:
    return ctx


def emit(ctx: Context, *, output: t.Optional[t.IO[str]] = None) -> None:
    loading.dump(ctx.result, output, format=ctx.config.option.output_format)
