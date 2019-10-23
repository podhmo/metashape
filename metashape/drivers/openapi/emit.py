from __future__ import annotations
import typing as t
import logging
import dataclasses
from functools import partial
from dictknife import loading
from metashape.langhelpers import make_dict, reify
from metashape.analyze import ModuleWalker, Member
from metashape.analyze import typeinfo
from metashape.analyze import Context as AnalyzingContext

from . import detect

logger = logging.getLogger(__name__)
Store = t.Dict[str, t.Any]

# TODO: some validations
# TODO: additionalProperties
# TODO: conflict name


class Context:  # TODO: rename to context?
    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Status:
        has_query: bool = False
        has_mutation: bool = False
        schemas: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        store: t.Dict[str, t.Any] = dataclasses.field(
            default_factory=lambda: make_dict(components=make_dict(schemas=make_dict()))
        )

    def __init__(self, walker: ModuleWalker) -> None:
        self.status = Context.Status()
        self.result = Context.Result()
        self.walker = walker
        self.internal = walker.context

    status: Context.Status
    result: Context.Result
    walker: ModuleWalker
    internal: AnalyzingContext


class _Fixer:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def fix_discriminator(self, name: str, fieldname: str) -> None:
        status = self.ctx.status
        schema = status.schemas.get(name)
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

    def _build_ref_data(self, field_type: t.Union[t.Type[t.Any], t.ForwardRef]) -> dict:
        resolver = self.ctx.walker.resolver
        return {
            "$ref": f"#/schemas/components/{resolver.resolve_name(field_type)}"
        }  # todo: lazy

    def _build_one_of_data(self, info: typeinfo.TypeInfo) -> dict:
        resolver = self.ctx.walker.resolver
        internalctx = self.ctx.walker.context
        candidates = []
        need_discriminator = True

        for x in info["args"]:
            if x["custom"] is None:
                need_discriminator = False
                candidates.append({"type": detect.schema_type(x)})
            else:
                candidates.append(self._build_ref_data(x["custom"]))
        prop = {"oneOf": candidates}  # todo: discriminator

        if need_discriminator:
            prop["discriminator"] = {"propertyName": self.DISCRIMINATOR_FIELD}
            # update schema
            for x in info["args"]:
                internalctx.callbacks.append(
                    partial(
                        self.fixer.fix_discriminator,
                        resolver.resolve_name(x["custom"]),
                        self.DISCRIMINATOR_FIELD,
                    )
                )
        return prop

    def scan(self, member: Member) -> None:
        ctx = self.ctx
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        internalctx = self.ctx.internal
        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        description = resolver.resolve_doc(member, verbose=internalctx.option.verbose)

        schema = make_dict(
            properties=properties, required=required, description=description
        )

        for field_name, field_type, metadata in walker.for_type(member).walk():
            logger.info(
                "walk prop: 	name=%r	type=%r	keys(metadata)=%s",
                field_name,
                field_type,
                (metadata or {}).keys(),
            )
            info = resolver.resolve_type_info(field_type)
            logger.debug("walk prop: 	info=%r", info)
            if not info["is_optional"]:
                required.append(field_name)

            # TODO: self recursion check (warning)
            if resolver.is_member(field_type):
                walker.append(field_type)

                properties[field_name] = self._build_ref_data(field_type)
                continue

            if info.get("is_composite", False):
                properties[field_name] = prop = self._build_one_of_data(info)
            else:
                prop = properties[field_name] = {"type": detect.schema_type(info)}
                enum = detect.enum(info)
                if enum:
                    prop["enum"] = enum

            if prop.get("type") == "array":  # todo: simplify with recursion
                assert len(info["args"]) == 1
                first = info["args"][0]
                if first.get("is_composite", False):
                    prop["items"] = self._build_one_of_data(first)
                elif first["custom"] is None:
                    prop["items"] = detect.schema_type(first)
                else:
                    custom_type = first["custom"]
                    prop["items"] = self._build_ref_data(custom_type)

        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        ctx.status.schemas[typename] = ctx.result.store["components"]["schemas"][
            typename
        ] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for m in walker.walk():
            logger.info("walk type: %r", m)
            scanner.scan(m)
    finally:
        ctx.internal.callbacks.teardown()  # xxx:
    return loading.dump(
        ctx.result.store, output, format=ctx.internal.option.output_format
    )
