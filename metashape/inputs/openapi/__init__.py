from __future__ import annotations
import typing as t
import logging
import dataclasses
import dictknife
from dictknife.langhelpers import make_dict

# TODO: flatten
# TODO: normalize name
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

    def resolve_python_type(self, name:str, d: AnyDict) -> t.Type[t.Any]:
        type_hints = {}
        for field_name, field in d["properties"].items():
            type_hints[field_name] = str  # TODO: guess type
        return type(name, (), {"__annotations__": type_hints})


class Accessor:
    def __init__(self, resolver: t.Optional[Resolver] = None):
        self.resolver = resolver or Resolver()

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


@dataclasses.dataclass
class Context:
    types: AnyDict = dataclasses.field(default_factory=make_dict)


def visit(ctx: Context, d: AnyDict) -> None:
    a = Accessor(Resolver(d))
    for name, sd in a.schemas(d):
        # TODO: normalize
        ctx.types[name] = a.resolver.resolve_python_type(name, sd)


def emit(ctx: Context):
    from prestring.python import Module

    m = Module()
    for name, cls in ctx.types.items():
        with m.class_(name):
            # TODO: omit class inheritance
            for field_name, field_type in t.get_type_hints(cls).items():
                # TODO: to pytype
                m.stmt(f"{field_name}: {field_type.__name__}")
    return m
