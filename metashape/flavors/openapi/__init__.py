import typing as t
from metashape.langhelpers import make_dict
from metashape.analyze import Accessor, Member


Store = t.Dict[str, t.Any]


def _make_store() -> Store:
    return make_dict(components=make_dict(schemas=make_dict()))


class Emitter:
    def __init__(self, accessor: Accessor, *, store: Store) -> None:
        self.accessor = accessor
        self.store = store

    def emit(self, member: Member, *, store=Store) -> None:
        resolver = self.accessor.resolver

        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        schema = make_dict(properties=properties, required=required)

        for fieldname, fieldtype in member.__annotations__.items():  # xxx
            # TODO: detect python type to openapi
            properties[fieldname] = make_dict(type=fieldtype.__name__)
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
    import json

    return json.dump(store, output, indent=2, ensure_ascii=False)
