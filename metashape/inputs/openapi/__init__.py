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

    def resolve_python_type(self, d: AnyDict, *, name: str,) -> t.Type[t.Any]:
        type_hints = {}
        for field_name, field in d["properties"].items():
            type_hints[field_name] = str  # TODO: guess type
        return type(name, (), {"__annotations__": type_hints})

    ##

    def has_ref(self, d: AnyDict) -> bool:
        return "$ref" in d

    def has_allof(self, d: AnyDict) -> bool:
        return "allOf" in d

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
    def __init__(self, resolver: Resolver):
        self.resolver = resolver

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

    def extract_python_type(self, name: str, d: AnyDict) -> t.Type[t.Any]:
        metadata_dict = self._extract_metadata_dict_pre_properties(d)
        type_hints = {}
        for field_name, field in d["properties"].items():
            metadata = metadata_dict[field_name]

            typ = str  # TODO: guess type
            if not metadata["required"]:
                typ = t.Optional[str]
            type_hints[field_name] = typ
        return type(name, (), {"__annotations__": type_hints})

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
    types: AnyDict = dataclasses.field(default_factory=make_dict)


class Emitter:
    def __init__(self, *, m: t.Optional[Module] = None) -> None:
        m = m or Module()
        self.m = m
        self.import_area = m.submodule()

    def _get_type_str(self, typ: t.Type[t.Any]) -> str:
        name = getattr(typ, "__name__", None)
        if name is None:
            if hasattr(typ, "__origin__"):
                name = typ.__origin__._name
        assert name is not None

        if typ.__module__ != "builtins":
            self.import_area.import_(typ.__module__)

        # TODO: implementation
        if hasattr(typ, "__args__"):
            return str(typ)
        else:
            return typ.__name__

    def emit(self, ctx: Context) -> Module:
        m = self.m

        for name, cls in ctx.types.items():
            with m.class_(name):
                # TODO: omit class inheritance
                for field_name, field_type in t.get_type_hints(cls).items():
                    # TODO: to pytype
                    type_str = self._get_type_str(field_type)
                    m.stmt(f"{field_name}: {type_str}")

        if str(self.import_area):
            self.import_area.sep()
        return m


def main(d: AnyDict) -> None:
    ctx = Context()
    resolver = Resolver(d)
    a = Accessor(resolver)
    for name, sd in a.schemas(d):
        if not a.resolver.has_schema(sd):
            logger.debug("skip schema %s", name)
            continue

        # TODO: normalize
        ctx.types[name] = a.extract_python_type(name, sd)

    emitter = Emitter()
    print(emitter.emit(ctx))
