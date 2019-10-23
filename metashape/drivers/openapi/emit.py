import typing as t
import logging
import dataclasses
from functools import partial
from metashape.langhelpers import make_dict, reify
from metashape.analyze import ModuleWalker, Member, Context
from metashape.analyze import typeinfo
from . import detect

logger = logging.getLogger(__name__)
Store = t.Dict[str, t.Any]

# TODO: some validations
# TODO: additionalProperties
# TODO: conflict name


class _State:  # TODO: rename to context?
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

    def __init__(self) -> None:
        self.status = _State.Status()
        self.result = _State.Result()


class _Fixer:
    def __init__(self, state: _State) -> None:
        self.state = state

    def fix_discriminator(self, name: str, fieldname: str) -> None:
        status = self.state.status
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

    def __init__(self, walker: ModuleWalker, *, state: _State) -> None:
        self.walker = walker
        self.state = state

    @reify
    def fixer(self) -> _Fixer:
        return _Fixer(self.state)

    def _build_ref_data(self, field_type: t.Union[t.Type[t.Any], t.ForwardRef]) -> dict:
        resolver = self.walker.resolver
        return {
            "$ref": f"#/schemas/components/{resolver.resolve_name(field_type)}"
        }  # todo: lazy

    def _build_one_of_data(self, info: typeinfo.TypeInfo) -> dict:
        resolver = self.walker.resolver
        ctx = self.walker.context
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
                ctx.callbacks.append(
                    partial(
                        self.fixer.fix_discriminator,
                        resolver.resolve_name(x["custom"]),
                        self.DISCRIMINATOR_FIELD,
                    )
                )
        return prop

    def scan(self, member: Member) -> None:
        walker = self.walker
        resolver = self.walker.resolver
        ctx = self.walker.context
        state = self.state

        typename = resolver.resolve_name(member)

        required = []
        properties = make_dict()
        description = resolver.resolve_doc(member, verbose=ctx.verbose)

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
                self.walker.append(field_type)

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
        state.status.schemas[typename] = state.result.store["components"]["schemas"][
            typename
        ] = schema


def emit(walker: ModuleWalker, *, output: t.IO[str]) -> None:
    state = _State()
    ctx = walker.context
    scanner = Scanner(walker, state=state)

    try:
        for m in walker.walk():
            logger.info("walk type: %r", m)
            scanner.scan(m)
    finally:
        ctx.callbacks.teardown()  # xxx:
    return ctx.dumper.dump(state.result.store, output, format="json")
