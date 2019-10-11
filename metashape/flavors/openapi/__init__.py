import typing as t
import json
from metashape.langhelpers import make_dict
from metashape.analyze import Accessor, Member

from . import resolve

# TODO: support format
# TODO: support description
# TDOO: support $ref
# TDOO: nested $ref
# TODO: t.Union -> oneOf with discriminator
# TODO: string literarl type -> enum


Store = t.Dict[str, t.Any]


def _make_store() -> Store:
    return make_dict(components=make_dict(schemas=make_dict()))


class Emitter:
    def __init__(self, accessor: Accessor, *, store: Store) -> None:
        self.accessor = accessor
        self.store = store

    def emit(self, member: Member, *, store=Store) -> None:
        resolver = self.accessor.resolver
        context = self.accessor.context

        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        description = resolver.resolve_description(member, verbose=context.verbose)

        schema = make_dict(
            properties=properties, required=required, description=description
        )

        for fieldname, fieldtype in resolver.resolve_annotations(member).items():
            prop = resolve.type_info(fieldtype, strict=context.strict)
            enum = resolve.enum(fieldtype)
            if enum:
                prop["enum"] = enum

            properties[fieldname] = prop

            if not prop.pop("optional"):
                required.append(fieldname)

        if len(required) <= 0:
            schema.pop("required")
        if not description:
            schema.pop("description")
        store["components"]["schemas"][typename] = schema


def emit(accessor: Accessor, *, output: t.IO) -> None:
    repository = accessor.repository

    store = _make_store()
    emitter = Emitter(accessor, store=store)
    for m in repository.members:
        emitter.emit(m, store=store)
    return json.dump(store, output, indent=2, ensure_ascii=False)
