from __future__ import annotations
import typing as t
import typing_extensions as tx
import logging
from collections import defaultdict
import dataclasses
import dictknife
from prestring.python import Module
from dictknife.langhelpers import make_dict

# TODO: flatten
# TODO: normalize name
# TODO: memorize original name
# TODO: support the name startswith reserved word
# TODO: support the name startswith emoji or number
# TODO: metashape like structure
# TODO: support schemas
# TODO: support required/unrequired
# TODO: support nullable
# - object
# - primitive
# - allOf

AnyDict = t.Dict[str, t.Any]
logger = logging.getLogger(__name__)


class Resolver:
    def __init__(self, fulldata: AnyDict) -> None:
        self.fulldata = fulldata
        self._accessor = dictknife.Accessor()  # todo: rename

    def has_ref(self, d: AnyDict) -> bool:
        return "$ref" in d

    def get_ref(self, d: AnyDict) -> str:
        return d["$ref"]

    def has_allof(self, d: AnyDict) -> bool:
        return "allOf" in d

    def has_array(self, d) -> bool:
        return d.get("type") == "array" or "items" in d

    def get_array_items(self, d) -> bool:
        return d["items"]

    def has_schema(
        self, d: AnyDict, cand: t.Tuple[str, ...] = ("object",), fullscan: bool = True,
    ) -> bool:
        typ = d.get("type", None)
        if typ in cand:
            return True
        if "properties" in d:
            return True
        if self.has_allof(d):
            return True
        if not self.has_ref(d):
            return False
        if not fullscan:
            return False

        # TODO: cache?
        _, definition = self.resolve_ref_definition(d)
        return self.has_schema(definition, fullscan=False)

    ##
    def resolve_ref_definition(
        self,
        d: t.Dict[str, t.Any],
        name: t.Optional[str] = None,
        i: int = 0,
        level: int = -1,
    ) -> t.Tuple[str, t.Dict[str, t.Any]]:
        # return schema_name, definition_dict
        # todo: support quoted "/"
        # on array
        if "items" in d:
            definition = d
            name, _ = self.resolve_ref_definition(
                d["items"], name=name, i=i, level=level + 1
            )  # xxx
            return name, definition

        if "$ref" not in d:
            return self.resolve_schema_name(name), d
        if level == 0:
            return self.resolve_schema_name(name), d

        logger.debug("    resolve: %sref=%r", "  " * i, d["$ref"])

        path = d["$ref"][len("#/") :].split("/")
        name = path[-1]

        parent = self._accessor.maybe_access_container(path)
        if parent is None:
            logger.warning("%r is not found", d["$ref"])
            return self.resolve_schema_name(name), d
        ref_name, definition = self.resolve_ref_definition(
            parent[name], name=name, i=i + 1, level=level - 1
        )

        # import for separated output
        # if X_MARSHMALLOW_INLINE not in definition:
        #     if c is not None and (
        #         "properties" in definition
        #         or (
        #             (
        #                 "additionalProperties" in definition
        #                 or "items" in definition
        #                 or "allOf" in definition
        #             )
        #             and self.has_schema(fulldata, definition)
        #         )
        #     ):
        #         c.relative_import_from_lazy(ref_name)
        return ref_name, definition


class Accessor:
    def __init__(self, resolver: Resolver, *, refs: t.Dict[str, Ref]):
        self.resolver = resolver
        self.refs = refs

    def schemas(self, d: AnyDict) -> t.Iterator[t.Tuple[str, AnyDict]]:
        try:
            components = d["components"]
        except KeyError:
            logger.info("skip, components is not found")
            return []
        try:
            schemas = components["schemas"]
        except KeyError:
            logger.info("skip, components/schemas is not found")
            return []

        for k, v in schemas.items():
            yield k, v

    def extract_type(self, name: str, d: AnyDict) -> Type:
        resolver = self.resolver
        metadata_dict = self._extract_metadata_dict_pre_properties(d)
        annotations = {}

        for field_name, field in d["properties"].items():
            metadata = metadata_dict[field_name]
            # TODO: see ref deeply
            if resolver.has_ref(field):
                annotations[field_name] = Ref(ref=resolver.get_ref(field))
                continue

            typ = Type(name="str")  # TODO: cache
            if resolver.has_array(field):
                typ = List(Ref(ref=resolver.get_ref(resolver.get_array_items(field))))
            if not metadata["required"]:
                typ = Optional(typ)
            annotations[field_name] = typ
        return Type(name=name, bases=(), annotations=annotations)

    def _extract_metadata_dict_pre_properties(
        self, d: t.Dict[str, t.Any]
    ) -> t.Dict[str, MetadataDict]:
        metadata_dict: t.Dict[str, MetadataDict] = defaultdict(
            lambda: {"required": False}
        )
        for field_name in d.get("required") or []:
            metadata_dict[field_name]["required"] = True
        return metadata_dict


class MetadataDict(tx.TypedDict, total=False):
    required: bool


@dataclasses.dataclass
class Context:
    import_area: Module
    types: t.Dict[str, Type] = dataclasses.field(default_factory=make_dict)
    refs: t.Dict[str, Ref] = dataclasses.field(default_factory=make_dict, compare=False)


@dataclasses.dataclass
class Ref:
    ref: str

    @property
    def name(self) -> str:
        return self.ref.rsplit("/", 1)[-1]

    def as_type_str(self, ctx: Context) -> str:
        name = self.name
        if name not in ctx.types:
            logger.info("as_type_str(): type %s is not found.", name)
            return f"TODO[{name}]"
        return ctx.types[name].as_type_str(ctx)


@dataclasses.dataclass
class Type:
    name: str
    bases: t.Tuple[str, ...] = dataclasses.field(default_factory=tuple)
    annotations: t.Dict[str, t.Union[Type, Ref]] = dataclasses.field(
        default_factory=make_dict, compare=False
    )
    module: str = ""

    def as_type_str(self, ctx: Context) -> str:
        if not self.module:
            return self.name

        ctx.import_area.import_(self.module)
        return f"{self.module}.{self.name}"


@dataclasses.dataclass
class Container:
    name: str
    module: str
    args: t.List[Type] = dataclasses.field(default_factory=list)

    def as_type_str(self, ctx: Context) -> str:
        # TODO: cache
        args = [x.as_type_str(ctx) for x in self.args]
        fullname = self.module
        if self.module:
            ctx.import_area.import_(self.module)
            fullname = f"{self.module}.{self.name}"
        return f"{fullname}[{', '.join(args)}]"


def Optional(typ: Type) -> Container:
    return Container(name="Optional", module="typing", args=[typ])


def List(typ: Type) -> Container:
    return Container(name="List", module="typing", args=[typ])


def Dict(k: Type, v: Type) -> Container:
    return Container(name="Dict", module="typing", args=[k, v])


class Emitter:
    def __init__(self, *, m: t.Optional[Module] = None) -> None:
        self.m = m or Module()

    def emit(self, ctx: Context) -> Module:
        m = self.m

        for name, typ in ctx.types.items():
            with m.class_(name):
                # TODO: omit class inheritance
                for field_name, field_type in typ.annotations.items():
                    # TODO: to pytype
                    type_str = field_type.as_type_str(ctx)
                    m.stmt(f"{field_name}: {type_str}")

        if str(ctx.import_area):
            ctx.import_area.sep()
        return m


def main(d: AnyDict) -> None:
    m = Module()
    ctx = Context(import_area=m.submodule())
    resolver = Resolver(d)
    a = Accessor(resolver, refs=ctx.refs)
    for name, sd in a.schemas(d):
        if not a.resolver.has_schema(sd):
            logger.debug("skip schema %s", name)
            continue

        # TODO: normalize
        ctx.types[name] = a.extract_type(name, sd)

    emitter = Emitter(m=m)
    print(emitter.emit(ctx))
