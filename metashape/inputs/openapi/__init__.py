from __future__ import annotations
import typing as t
import typing_extensions as tx
from collections import defaultdict, deque
import logging
import re
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
# TODO: support list
# TODO: support list inline
# TODO: support list ref
# TODO: support list nested
# - object
# - primitive
# - allOf

AnyDict = t.Dict[str, t.Any]
logger = logging.getLogger(__name__)


class Resolver:
    def __init__(self, fulldata: AnyDict, *, refs: t.Dict[str, Ref]) -> None:
        self.fulldata = fulldata
        self.refs = refs
        self._accessor = dictknife.Accessor()  # todo: rename
        self._origin_defs: t.Dict[str, t.Tuple[str, AnyDict]] = {}

    def resolve_normalized_name(self, name: str) -> str:
        return normalize(name)

    def resolve_schema_name(self, name: str) -> str:
        return titleize(name)

    def has_ref(self, d: AnyDict) -> bool:
        return "$ref" in d

    def get_ref(self, d: AnyDict) -> str:
        return d["$ref"]

    def resolve_ref(self, ref: str) -> t.Tuple[str, AnyDict]:  # shallow
        # ref format is "#/components/schemas/<name>"
        # todo: cache
        path = ref[len("#/") :].split("/")
        name = path[-1]
        source = self._accessor.maybe_access_container(self.fulldata, path)
        return name, source

    def has_allof(self, d: AnyDict) -> bool:
        return "allOf" in d

    def has_array(self, d) -> bool:
        return d.get("type") == "array" or "items" in d

    def get_array_items(self, d) -> bool:
        return d["items"]

    def has_object(self, d, cand: t.Tuple[str, ...] = ("object",)) -> bool:
        typ = d.get("type", None)
        if typ in cand:
            return True
        if self.has_allof(d):
            return True
        return False


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
                for field_name, field_type in typ.annotations.items():
                    # TODO: to pytype
                    type_str = field_type.as_type_str(ctx)
                    m.stmt(f"{field_name}: {type_str}")

        if str(ctx.import_area):
            ctx.import_area.sep()
        return m


# langhelpers
def normalize(name: str, ignore_rx: re.Pattern = re.compile("[^0-9a-zA-Z_]+")) -> str:
    c = name[0]
    if c.isdigit():
        name = "n" + name
    elif not (c.isalpha() or c == "_"):
        name = "x" + name
    return ignore_rx.sub("", name.replace("-", "_"))


def titleize(name: str) -> str:
    if not name:
        return name
    name = str(name)
    return normalize("{}{}".format(name[0].upper(), name[1:]))


# TODO: allOf,oneOf,anyOf
GUESS_KIND = tx.Literal["?", "object", "array", "ref", "primitive"]


def main(d: AnyDict) -> None:
    logging.basicConfig(level=logging.INFO)  # debug

    m = Module()
    ctx = Context(import_area=m.submodule())
    resolver = Resolver(d, refs=ctx.refs)
    a = Accessor(resolver)

    seen: t.Set[str] = set()
    q: t.Deque[t.Tuple[GUESS_KIND, name, AnyDict, t.List[t.Tuple[str, str]]]] = deque()
    for name, sd in a.schemas(d):
        q.append(("?", name, sd, []))

    try:
        while len(q) > 0:
            guess_kind, name, sd, history = q.popleft()
            history.append((guess_kind, name))
            if guess_kind == "?":
                if resolver.has_ref(sd):
                    q.append(("ref", name, sd, history))
                elif resolver.has_array(sd):
                    q.append(("array", name, sd, history))
                elif resolver.has_object(sd):
                    q.append(("object", name, sd, history))
                else:
                    q.append(("primitive", name, sd, history))
                continue

            # if name in seen:
            #     continue
            # seen.add(name)

            if guess_kind == "ref":
                ref = resolver.get_ref(sd)
                ctx.refs[name] = Ref(ref=ref)
                new_name, new_sd = resolver.resolve_ref(ref)
                logger.debug("enqueue: ref %s as %s", name, new_name)
                q.append(("?", new_name, new_sd, history))
            elif guess_kind == "array":
                # todo: save array?, todo: cache
                if resolver.has_array(sd):
                    logger.debug("enqueue: array item %s", name)
                    new_sd = resolver.get_array_items(sd)
                    q.append(("?", name + "Item", new_sd, history))
                logger.info("skip: array %r is skipped", name)
            elif guess_kind == "object":
                ctx.types[name] = a.extract_type(name, sd)
            elif guess_kind == "primitive":
                logger.info("skip: primitive %r is skipped", name)
            else:
                raise ValueError(f"unexpected guess kind {guess_kind}, name={name}")
    except Exception as e:
        # TODO: only DEBUG=1
        import json

        logger.warning(
            "hmm.. %r. in guess_kind=%s, name=%s, history=%s, data=%s",
            e,
            guess_kind,
            name,
            history,
            json.dumps(sd, indent=2),
        )
        raise
    emitter = Emitter(m=m)
    print(emitter.emit(ctx))
