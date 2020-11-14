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

    # for python
    def resolve_pytype_str(self, typ: t.Type[t.Any]) -> str:
        # TODO: implementation
        if hasattr(typ, "__args__"):
            return str(typ)
        else:
            return typ.__name__

    # for dict


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
    def __init__(self, resolver: Resolver) -> None:
        self.resolver = resolver

    def emit(self, ctx: Context) -> Module:
        m = Module()
        for name, cls in ctx.types.items():
            with m.class_(name):
                # TODO: omit class inheritance
                for field_name, field_type in t.get_type_hints(cls).items():
                    # TODO: to pytype
                    type_str = self.resolver.resolve_pytype_str(field_type)
                    m.stmt(f"{field_name}: {type_str}")
        return m


def main(d: AnyDict) -> None:
    ctx = Context()
    resolver = Resolver(d)
    a = Accessor(resolver)
    for name, sd in a.schemas(d):
        # TODO: normalize
        ctx.types[name] = a.extract_python_type(name, sd)

    emitter = Emitter(resolver)
    print(emitter.emit(ctx))
