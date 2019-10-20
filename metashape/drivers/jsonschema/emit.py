import typing as t
import logging
from functools import partial
from metashape.langhelpers import make_dict
from metashape.analyze import Walker, Member, Context
from metashape.analyze import typeinfo
from . import detect

logger = logging.getLogger(__name__)
Store = t.Dict[str, t.Any]

# TODO: some validations
# TODO: additionalProperties
# TODO: conflict name
# TODO: type defined by array
# TODO: toplevel definitions
# TODO: drop discriminator


class Emitter:
    DISCRIMINATOR_FIELD = "$type"

    def __init__(self, walker: Walker, ctx: Context) -> None:
        self.walker = walker
        self.ctx = ctx

        self._schemas = {}
        self.callbacks = []

    def teardown(self) -> None:
        callbacks, self.callbacks = self.callbacks, []
        for callback in callbacks:
            callback()

    def _as_discriminator(self, name: str, fieldname: str) -> None:
        schema = self._schemas.get(name)
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

    def _build_ref_data(self, field_type: t.Union[t.Type[t.Any], t.ForwardRef]) -> dict:
        resolver = self.walker.resolver
        return {
            "$ref": f"#/definitions/{resolver.resolve_name(field_type)}"
        }  # todo: lazy

    def _build_one_of_data(self, info: typeinfo.TypeInfo) -> dict:
        resolver = self.walker.resolver
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
                self.callbacks.append(
                    partial(
                        self._as_discriminator,
                        resolver.resolve_name(x["custom"]),
                        self.DISCRIMINATOR_FIELD,
                    )
                )
        return prop

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
        self._schemas[typename] = store["definitions"][typename] = schema


def emit(walker: Walker, *, output: t.IO[str]) -> None:
    store = make_dict(definitions=make_dict())
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
    return ctx.dumper.dump(store, output, format="json")
