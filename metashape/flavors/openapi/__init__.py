import typing as t
import json
import logging
from metashape.langhelpers import make_dict
from metashape.analyze.walker import Walker, Member
from . import detect

logger = logging.getLogger(__name__)

# TODO: support format
# TODO: t.Union -> oneOf with discriminator


Store = t.Dict[str, t.Any]


class Emitter:
    def __init__(self, walker: Walker) -> None:
        self.walker = walker

    def emit(self, member: Member, *, store=Store) -> None:
        walker = self.walker
        resolver = self.walker.resolver
        context = self.walker.context

        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        description = resolver.resolve_doc(member, verbose=context.verbose)

        schema = make_dict(
            properties=properties, required=required, description=description
        )

        for fieldname, fieldtype, metadata in walker.walk_type(member):
            logger.info(
                "walk prop: 	name=%r	type=%r	keys(metadata)=%s",
                fieldname,
                fieldtype,
                (metadata or {}).keys(),
            )
            info = resolver.resolve_type_info(fieldtype)
            logger.debug("walk prop: 	info=%r", info)
            if not info["is_optional"]:
                required.append(fieldname)

            # TODO: self recursion check (warning)
            if resolver.is_member(fieldtype):
                self.walker.q.append(fieldtype)

                properties[fieldname] = {
                    "$ref": f"#/schemas/components/{resolver.resolve_name(fieldtype)}"
                }  # todo: lazy
                continue

            # todo: array support
            prop = properties[fieldname] = {"type": detect.schema_type(info)}
            enum = detect.enum(info)
            if enum:
                prop["enum"] = enum

        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        store["components"]["schemas"][typename] = schema


def emit(walker: Walker, *, output: t.IO) -> None:
    store = make_dict(components=make_dict(schemas=make_dict()))
    emitter = Emitter(walker)

    for m in walker.walk_module():
        walker.q.append(m)

    while True:
        try:
            m = walker.q.popleft()
            logger.info("walk type: %r", m)
            emitter.emit(m, store=store)
        except IndexError:
            break
    return json.dump(store, output, indent=2, ensure_ascii=False)
