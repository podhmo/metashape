from __future__ import annotations
import typing as t
import logging
import dataclasses
from dictknife import loading
from metashape.types import Member, _ForwardRef
from metashape.langhelpers import make_dict
from metashape.analyze import typeinfo
from metashape.analyze.walker import ModuleWalker
from metashape.analyze.context import Context as AnalyzingContext
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
    class Status:
        has_query: bool = False
        has_mutation: bool = False
        schemas: t.Dict[str, t.Any] = dataclasses.field(default_factory=make_dict)

    @dataclasses.dataclass(frozen=False, unsafe_hash=True)
    class Result:
        store: t.Dict[str, t.Any] = dataclasses.field(
            default_factory=lambda: make_dict(definitions=make_dict())
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


class Scanner:
    ctx: Context

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def _build_ref_data(
        self, field_type: t.Union[t.Type[t.Any], _ForwardRef]
    ) -> t.Dict[str, t.Any]:
        resolver = self.ctx.walker.resolver
        return {
            "$ref": f"#/definitions/{resolver.resolve_name(field_type)}"
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

    def scan(self, member: Member) -> None:
        ctx = self.ctx
        walker = self.ctx.walker
        resolver = self.ctx.walker.resolver
        internalctx = self.ctx.internal

        typename = resolver.resolve_name(member)

        required: t.List[str] = []
        properties: t.Dict[str, t.Any] = make_dict()
        description = resolver.resolve_doc(member, verbose=internalctx.option.verbose)

        schema: t.Dict[str, t.Any] = make_dict(
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
            if not info.is_optional:
                required.append(field_name)

            # TODO: self recursion check (warning)
            if resolver.is_member(field_type):
                walker.append(field_type)

                properties[field_name] = self._build_ref_data(field_type)
                continue

            if typeinfo.is_composite(info):
                properties[field_name] = prop = self._build_one_of_data(info)
            else:
                prop = properties[field_name] = {"type": detect.schema_type(info)}
                enum = detect.enum(info)
                if enum:
                    prop["enum"] = enum

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
        ctx.status.schemas[typename] = ctx.result.store["definitions"][
            typename
        ] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    ctx = Context(walker)
    scanner = Scanner(ctx)

    try:
        for m in walker.walk(ignore_private=ctx.internal.option.ignore_private):
            logger.info("walk type: %r", m)
            scanner.scan(m)
    finally:
        ctx.internal.callbacks.teardown()  # xxx:
    loading.dump(ctx.result.store, output, format=ctx.internal.option.output_format)
