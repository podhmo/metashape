import typing as t
import logging
from metashape.langhelpers import make_dict
from metashape.analyze import Walker, Member, Context

# from metashape.analyze import typeinfo
from . import detect

logger = logging.getLogger(__name__)
Store = t.Dict[str, t.Any]


class Emitter:
    def __init__(self, walker: Walker, ctx: Context) -> None:
        self.walker = walker
        self.ctx = ctx

        self._types = {}
        self.callbacks = []

    def teardown(self) -> None:
        callbacks, self.callbacks = self.callbacks, []
        for callback in callbacks:
            callback()

    def emit(self, member: Member, *, store=Store) -> None:
        walker = self.walker
        resolver = self.walker.resolver
        ctx = self.ctx

        schema = make_dict()
        typename = resolver.resolve_name(member)

        for field_name, field_type, metadata in walker.walk_type(member):
            logger.info(
                "walk prop: 	name=%r	type=%r	keys(metadata)=%s",
                field_name,
                field_type,
                (metadata or {}).keys(),
            )
            info = resolver.resolve_type_info(field_type)
            logger.debug("walk prop: 	info=%r", info)
            prop = schema[field_name] = {"type": detect.schema_type(info)}
            if not info["is_optional"]:
                prop["type"] = f"!{prop['type']}"

        self._types[typename] = store["types"][typename] = schema


def emit(walker: Walker, *, output: t.IO[str]) -> None:
    store = make_dict(types=make_dict())
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
    emitter.teardown()  # xxx:
    Dumper().dump(store, output)  # xxx


class Dumper:
    def dump(self, store, o: t.IO[str]) -> None:
        print("schema {", file=o)
        for name in store["types"]:
            print(f"  {name}: {name}", file=o)  # lower?
        print("}", file=o)
        print("", file=o)

        print("type Query {", file=o)
        print("}", file=o)
        print("", file=o)

        for name, definition in store["types"].items():
            print(f"type {name} {{", file=o)
            for fieldname, fieldvalue in definition.items():
                print(f"  {fieldname}: {fieldvalue['type']}", file=o)
            print("}", file=o)
