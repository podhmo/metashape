from __future__ import annotations
import typing as t
import logging
import dataclasses
from functools import partial
from dictknife import loading
from metashape.types import Member, _ForwardRef
from metashape.langhelpers import make_dict, reify
from metashape.typeinfo import TypeInfo
from metashape.analyze.walker import Walker
from metashape.analyze.config import Config as AnalyzingConfig

from . import detect

logger = logging.getLogger(__name__)

# TODO: some validations
# TODO: additionalProperties
# TODO: conflict name


class Context:  # TODO: rename to context?
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class State:
        schemas: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)
        refs: t.Dict[t.Type[t.Any], t.Dict[str, str]] = dataclasses.field(
            default_factory=make_dict
        )

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        result: t.Dict[str, t.Any] = dataclasses.field(
            default_factory=lambda: make_dict(components=make_dict(schemas=make_dict()))
        )

    def __init__(self, walker: Walker) -> None:
        self.state = Context.State()
        self.result = Context.Result()
        self.walker = walker
        self.config = walker.config

    state: Context.State
    result: Context.Result
    walker: Walker
    config: AnalyzingConfig

    @property
    def verbose(self) -> bool:
        return self.config.option.verbose


class _Fixer:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def fix_discriminator(self, name: str, fieldname: str) -> None:
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

    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    @reify
    def fixer(self) -> _Fixer:
        return _Fixer(self.ctx)

    def _build_ref_data(
        self, field_type: t.Union[t.Type[t.Any], _ForwardRef]
    ) -> t.Dict[str, t.Any]:
        resolver = self.ctx.walker.resolver
        return {
            "$ref": f"#/components/schemas/{resolver.resolve_typename(field_type)}"
        }  # todo: lazy

    def _build_one_of_data(self, info: TypeInfo) -> t.Dict[str, t.Any]:
        resolver = self.ctx.walker.resolver
        cfg = self.ctx.walker.config
        candidates: t.List[t.Dict[str, t.Any]] = []
        need_discriminator = True

        for x in info.args:
            user_defined_type = x.user_defined_type
            if user_defined_type is None:
                need_discriminator = False
                candidates.append({"type": detect.schema_type(x)})
            else:
                candidates.append(self._build_ref_data(user_defined_type))
        prop: t.Dict[str, t.Any] = {"oneOf": candidates}  # todo: discriminator

        if need_discriminator:
            prop["discriminator"] = {"propertyName": self.DISCRIMINATOR_FIELD}
            # update schema
            for x in info.args:
                user_defined_type = x.user_defined_type
                if user_defined_type is None:
                    continue
                cfg.callbacks.append(
                    partial(
                        self.fixer.fix_discriminator,
                        resolver.resolve_typename(user_defined_type),
                        self.DISCRIMINATOR_FIELD,
                    )
                )
        return prop

    def scan(self, cls: Member) -> None:
        ctx = self.ctx
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        cfg = self.ctx.config
        typename = resolver.resolve_typename(cls)

        required: t.List[str] = []
        properties: t.Dict[str, t.Any] = make_dict()
        description: str = resolver.metadata.resolve_doc(cls, verbose=ctx.verbose)

        schema: t.Dict[str, t.Any] = make_dict(
            type="object",
            properties=properties,
            required=required,
            description=description,
        )

        for field_name, info, metadata in walker.for_type(cls).walk():
            field_name = resolver.metadata.resolve_name(metadata, default=field_name)
            if not info.is_optional:
                required.append(field_name)

            # TODO: self recursion check (warning)
            if resolver.is_member(info.type_) and resolver.resolve_typename(info.type_):
                walker.append(info.type_)

                properties[field_name] = self._build_ref_data(info.type_)
                continue

            if info.is_combined:
                properties[field_name] = prop = self._build_one_of_data(info)
            else:
                prop = properties[field_name] = {"type": detect.schema_type(info)}
                enum = detect.enum(info)
                if enum:
                    prop["enum"] = enum

            # default
            if resolver.metadata.has_default(metadata):
                prop["default"] = resolver.metadata.resolve_default(metadata)
            resolver.metadata.fill_extra_metadata(prop, metadata, name="openapi")

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
                        prop["format"] = info.supertypes[0].__name__.replace("_", "-")

        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        if cfg.option.strict and "additionalProperties" not in schema:
            schema["additionalProperties"] = False

        ctx.state.schemas[typename] = ctx.result.result["components"]["schemas"][
            typename
        ] = schema
        ctx.state.refs[cls] = {"$ref": f"#/components/schemas/{typename}"}


def scan(walker: Walker,) -> Context:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for cls in walker.walk():
            scanner.scan(cls)
    finally:
        ctx.config.callbacks.teardown()  # xxx:
    return ctx


def emit(ctx: Context, *, output: t.Optional[t.IO[str]] = None) -> None:
    loading.dump(ctx.result.result, output, format=ctx.config.option.output_format)
