import typing as t
import logging
from metashape.langhelpers import make_dict
from metashape.analyze import Walker, Member, Context
from . import detect

logger = logging.getLogger(__name__)

# TODO: support format
# TODO: t.Union -> oneOf with discriminator


Store = t.Dict[str, t.Any]


class Emitter:
    def __init__(self, walker: Walker, ctx: Context) -> None:
        self.walker = walker
        self.ctx = ctx

    def emit(self, member: Member, *, store=Store) -> None:
        walker = self.walker
        resolver = self.walker.resolver
        ctx = self.ctx

        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        description = resolver.resolve_doc(member, verbose=ctx.verbose)

        schema = make_dict(
            properties=properties, required=required, description=description
        )

        for field_name, field_type, metadata in walker.walk_type(member):
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
                self.ctx.q.append(field_type)

                properties[field_name] = {
                    "$ref": f"#/schemas/components/{resolver.resolve_name(field_type)}"
                }  # todo: lazy
                continue

            # todo: array support
            prop = properties[field_name] = {"type": detect.schema_type(info)}
            enum = detect.enum(info)
            if enum:
                prop["enum"] = enum
            if prop["type"] == "array":
                if info["args"][0]["custom"] is None:
                    prop["items"] = detect.schema_type(info["args"][0])
                else:
                    custom_type = info["args"][0]["custom"]
                    prop["items"] = {
                        "$ref": f"#/schemas/components/{resolver.resolve_name(custom_type)}"
                    }  # todo: lazy

        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        store["components"]["schemas"][typename] = schema


def emit(walker: Walker, *, output: t.IO[str]) -> None:
    store = make_dict(components=make_dict(schemas=make_dict()))
    ctx = walker.context
    emitter = Emitter(walker, ctx)

    for m in walker.walk_module():
        ctx.q.append(m)

    while True:
        try:
            m = ctx.q.popleft()
            logger.info("walk type: %r", m)
            emitter.emit(m, store=store)
        except IndexError:
            break
    return ctx.dumper.dump(store, output, format="json")
