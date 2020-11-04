from __future__ import annotations
import typing as t
import typing_extensions as tx
import logging
import dataclasses
from functools import partial
from dictknife import loading
from metashape.types import Member, MetaData
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


def scan(walker: Walker,) -> Context:
    ctx = Context(walker)
    builder = Builder(ctx, walker=walker)

    try:
        for cls in walker.walk():
            schema = builder.build_schema_data(cls)
            ctx.register_schema(cls, schema)
    finally:
        ctx.config.callbacks.teardown()  # xxx:
    return ctx


def emit(ctx: Context, *, output: t.Optional[t.IO[str]] = None) -> None:
    loading.dump(ctx.result, output, format=ctx.config.option.output_format)


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
        refs: t.Dict[t.Type[t.Any], RefDict] = dataclasses.field(
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
    # required
    type: detect.JSONSchemaType

    # optional
    description: str
    default: t.Any
    properties: t.Dict[str, t.Union[PropertyDict, RefDict, OneOfDict]]
    required: t.List[str]
    additionalProperties: t.Union[bool, t.Dict[str, t.Any]]


class OneOfDict(tx.TypedDict, total=False):
    # required
    oneOf: t.List[t.Union[RefDict, t.Dict[str, t.Any]]]

    # optional
    discriminator: t.Dict[str, str]  # {PropertyName:str}


RefDict = tx.TypedDict("RefDict", {"$ref": str})


class PropertyDict(tx.TypedDict, total=False):
    # required
    type: detect.JSONSchemaType

    # optional
    format: str
    default: t.Any
    description: str
    enum: t.Sequence[t.Any]

    # only type=array
    items: t.Union[RefDict, OneOfDict, t.Dict[str, t.Any]]


class _Fixer:
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


class Builder:
    DISCRIMINATOR_FIELD = "$type"

    def __init__(self, ctx: Context, *, walker: Walker) -> None:
        self.ctx = ctx
        self.walker = walker

    @reify
    def fixer(self) -> _Fixer:
        return _Fixer(self.ctx, discriminator_name=self.DISCRIMINATOR_FIELD)

    def build_ref_data(self, field_type: Member) -> RefDict:
        ref_data = self.ctx.state.refs.get(field_type)
        if ref_data is not None:
            return ref_data

        resolver = self.ctx.resolver
        self.walker.append(field_type)
        return {
            "$ref": f"#/components/schemas/{resolver.resolve_typename(field_type)}"
        }  # todo: lazy

    def build_one_of_data(self, info: TypeInfo) -> OneOfDict:
        candidates: t.List[t.Union[RefDict, t.Dict[str, detect.JSONSchemaType]]] = []
        need_discriminator = True

        for x in info.args:
            if x.user_defined_type is None:
                need_discriminator = False
                candidates.append({"type": detect.schema_type(x)})
            else:
                candidates.append(self.build_ref_data(x.user_defined_type))

        prop: OneOfDict = {"oneOf": candidates}
        if need_discriminator:
            prop["discriminator"] = {"propertyName": self.DISCRIMINATOR_FIELD}
            self.fixer.register_fix_discriminator_callback(info)
        return prop

    def build_property_data(
        self, info: TypeInfo, *, metadata: MetaData
    ) -> t.Union[PropertyDict, RefDict]:
        resolver = self.ctx.resolver
        metadata_resolver = resolver.metadata

        # TODO: self recursion check (warning)
        if (
            resolver.is_member(info.type_)
            or (
                info.user_defined_type is not None
                and not info.is_container
                and not info.is_newtype
            )
        ) and resolver.resolve_typename(info.type_):
            return self.build_ref_data(info.type_)

        prop: PropertyDict = make_dict()
        if info.is_combined:
            prop.update(self.build_one_of_data(info))  # type: ignore
        else:
            prop["type"] = detect.schema_type(info)
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

        # inject extra data
        metadata_resolver.fill_extra_metadata(
            prop, metadata, name="openapi"  # type:ignore
        )

        if prop.get("type") == "array":  # todo: simplify with recursion
            assert len(info.args) == 1
            first = info.args[0]
            if first.is_combined and first.is_container:
                prop["items"] = self.build_one_of_data(first)
            elif first.user_defined_type is None:
                prop["items"] = {"type": detect.schema_type(first)}
            else:
                if first.user_defined_type is not None:
                    prop["items"] = self.build_ref_data(first.user_defined_type)

        if info.is_newtype:
            if info.user_defined_type is not None:
                if prop.get("type") == "object":
                    return self.build_ref_data(info.user_defined_type)
            else:
                if hasattr(info.supertypes[0], "__name__"):
                    prop["format"] = resolver.resolve_typeformat(info)

        if info.container_type == "dict":
            prop["additionalProperties"] = self.build_property_data(
                info.args[1], metadata={}
            )

        return prop

    def build_schema_data(self, cls: Member) -> SchemaDict:
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

            properties[field_name] = self.build_property_data(info, metadata=metadata)

        # simplify
        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        if ctx.strict and "additionalProperties" not in schema:
            schema["additionalProperties"] = False
        return schema
