import typing as t
import json
from metashape.langhelpers import make_dict
from metashape.analyze import Accessor, Member
from . import detect

# TODO: support format
# TODO: support description
# TDOO: support $ref
# TDOO: nested $ref
# TODO: t.Union -> oneOf with discriminator
# TODO: string literarl type -> enum


Store = t.Dict[str, t.Any]


class Emitter:
    def __init__(self, accessor: Accessor, *, store: Store) -> None:
        self.accessor = accessor
        self.store = store

    def emit(self, member: Member, *, store=Store) -> None:
        resolver = self.accessor.resolver
        walker = self.accessor.walker
        context = self.accessor.context

        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        description = resolver.resolve_doc(member, verbose=context.verbose)

        schema = make_dict(
            properties=properties, required=required, description=description
        )

        for fieldname, fieldtype, metadata in walker.walk_type(member):
            info = resolver.resolve_type_info(fieldtype)
            if not info["is_optional"]:
                required.append(fieldname)

            # TODO: self recursion check (warning)
            if resolver.is_member(fieldtype):
                self.accessor.q.append(fieldtype)

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


def emit(accessor: Accessor, *, output: t.IO) -> None:
    walker = accessor.walker

    store = make_dict(components=make_dict(schemas=make_dict()))
    emitter = Emitter(accessor, store=store)

    for m in walker.walk_module():
        accessor.q.append(m)

    while True:
        try:
            emitter.emit(m, store=store)
            m = accessor.q.popleft()
        except IndexError:
            break
    return json.dump(store, output, indent=2, ensure_ascii=False)
