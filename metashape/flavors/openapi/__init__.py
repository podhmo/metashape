import typing as t
import json
from metashape.langhelpers import make_dict
from metashape.analyze import Accessor, Member

# TODO: support format
# TODO: support description
# TDOO: support $ref
# TDOO: nested $ref
# TODO: t.Union -> oneOf with discriminator
# TODO: string literarl type -> enum


Store = t.Dict[str, t.Any]


def _make_store() -> Store:
    return make_dict(components=make_dict(schemas=make_dict()))


def resolve_type(val: t.Type, *, strict: bool = True) -> t.Dict[str, t.Any]:
    if issubclass(val, str):
        return {"type": "string"}
    elif issubclass(val, bool):
        return {"type": "boolean"}
    elif issubclass(val, int):
        return {"type": "integer"}
    elif issubclass(val, float):
        return {"type": "number"}
    elif hasattr(val, "keys"):
        return {"type": "object"}
    elif issubclass(val, (list, tuple)):
        return {"type": "array"}
    elif strict:
        raise ValueError("unsupported for {!r}".format(val))
    else:
        return {}


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
        schema = make_dict(properties=properties, required=required)

        for fieldname, fieldtype in member.__annotations__.items():  # xxx
            # TODO: detect python type to openapi
            properties[fieldname] = resolve_type(fieldtype, strict=context.strict)
            # TODO: optional support
            required.append(fieldname)

        if len(required) <= 0:
            schema.pop("required")
        store["components"]["schemas"][typename] = schema


def emit(accessor: Accessor, *, output: t.IO) -> None:
    repository = accessor.repository

    store = _make_store()
    emitter = Emitter(accessor, store=store)
    for m in repository.members:
        emitter.emit(m, store=store)
    return json.dump(store, output, indent=2, ensure_ascii=False)
