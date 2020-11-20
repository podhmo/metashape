from __future__ import annotations
import typing as t
import typing_extensions as tx
import sys
import logging
import dataclasses
import dictknife
from functools import partial
from collections import defaultdict, deque, Counter, namedtuple
from prestring.python import Module
from dictknife.langhelpers import make_dict
from metashape.langhelpers import titleize, normalize

# TODO: metashape compatible output
# TODO: support nullable
# TODO: support array -- primitive
# TODO: additionalProperties as dict -- primitive
# TODO: additionalProperties as dict -- object
# TODO: additionalProperties as class
# TODO: primitive type with validation
# TODO: array type with validation
# TODO: handling type and format
# - primitive
# - allOf

AnyDict = t.Dict[str, t.Any]
# TODO: allOf,oneOf,anyOf
GUESS_KIND = tx.Literal["?", "object", "array", "ref", "primitive", "dict"]

logger = logging.getLogger(__name__)


class Accessor:
    def __init__(
        self, resolver: Resolver, *, enqueue: t.Callable[[t.Any], None],
    ):
        self.resolver = resolver
        self._enqueue = enqueue

    def iterate_schemas(self, d: AnyDict) -> t.Iterator[t.Tuple[str, AnyDict]]:
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

    def extract_object_type(self, name: str, d: AnyDict) -> Type:
        metadata_dict = self._extract_metadata_dict_pre_properties(d)
        annotations: t.Dict[str, t.Union[Repr, Type, Ref, Container]] = {}

        for field_name, field in (d.get("properties") or {}).items():
            metadata = metadata_dict[field_name]
            typ = self._extract_field_type(
                field_name, field, metadata=metadata, object_name=name
            )
            typ.metadata.update(metadata)
            annotations[field_name] = typ

        typ = Type(
            name=self.resolver.resolve_type_name(name),
            bases=(),
            annotations=annotations,
        )
        typ.metadata.update(
            [(k, v) for k, v in d.items() if k not in ("properties", "required")]  # type: ignore
        )
        return typ

    def _extract_field_type(
        self,
        field_name: str,
        field: AnyDict,
        *,
        metadata: MetadataDict,
        object_name: str,
    ) -> t.Union[Repr, Type, Ref, Container]:
        typ: t.Union[Repr, Type, Ref, Container]
        resolver = self.resolver
        if resolver.has_ref(field):
            typ = ref = Ref(ref=resolver.get_ref(field))
            ref_name = ref.name
            logger.debug(
                "enqueue: ref %s in extract_type %s.%s",
                ref_name,
                object_name,
                field_name,
            )
            self._enqueue(("ref", ref_name, field, []))
            return typ
        elif resolver.has_array(field):
            sub_name = f"{object_name}{resolver.resolve_type_name(field_name)}"
            items = resolver.get_array_items(field)
            if resolver.has_ref(items):
                ref = Ref(ref=resolver.get_ref(items))
                typ = List(ref)
                typ.metadata.update([(k, v) for k, v in field.items() if k != "items"])  # type: ignore
            else:
                ref = Ref(ref=sub_name, inline=True)
                typ = ref

            logger.debug(
                "enqueue: array %s in extract_type %s.%s",
                sub_name,
                object_name,
                field_name,
            )
            self._enqueue(("?", sub_name, field, []))
            return typ
        elif resolver.has_dict(field):
            additional_properties = resolver.get_dict_addtional_properties(field)
            sub_name = f"{object_name}{resolver.resolve_type_name(field_name)}"
            if resolver.has_ref(additional_properties):
                ref = Ref(ref=resolver.get_ref(additional_properties))
                typ = Dict(Type(name="str"), ref)
                typ.metadata.update(
                    [(k, v) for k, v in field.items() if k != "additionalProperties"]  # type: ignore
                )
            else:
                ref = Ref(ref=sub_name, inline=True)
                typ = ref
            logger.debug(
                "enqueue: array %s in extract_type %s.%s",
                sub_name,
                object_name,
                field_name,
            )
            self._enqueue(("?", sub_name, field, []))
            return typ
        elif resolver.has_object(field):
            sub_name = f"{object_name}{resolver.resolve_type_name(field_name)}"
            ref = Ref(ref=sub_name, inline=True)
            typ = ref
            logger.debug(
                "enqueue: object %s in extract_type %s.%s",
                sub_name,
                object_name,
                field_name,
            )
            self._enqueue(("object", sub_name, field, []))
            return typ
        else:
            return resolver.resolve_type(field, name=field_name)

    def _extract_metadata_dict_pre_properties(
        self, d: t.Dict[str, t.Any]
    ) -> t.Dict[str, MetadataDict]:
        metadata_dict: t.Dict[str, MetadataDict] = defaultdict(
            lambda: {"required": False}
        )
        for field_name in d.get("required") or []:
            metadata_dict[field_name]["required"] = True
        return metadata_dict


class Resolver:
    def __init__(self, fulldata: AnyDict, *, refs: t.Dict[str, Ref]) -> None:
        self.fulldata = fulldata
        self.refs = refs
        self._accessor = dictknife.Accessor()  # todo: rename
        self._origin_defs: t.Dict[str, t.Tuple[str, AnyDict]] = {}

        self._type_guesser = TypeGuesser()

    def resolve_type(self, d: AnyDict, *, name: str = "") -> t.Union[Type, Container]:
        if "enum" in d:
            typ = Literal([Repr(x) for x in d["enum"] if x is not None])
            typ.metadata.update(d)  # type: ignore
            return typ
        else:
            pair = self._resolve_format_pair(d, name=name)
            return self._type_guesser.guess_type(pair, field=d)

    def _resolve_format_pair(self, field: t.Dict[str, t.Any], *, name: str) -> Pair:
        try:
            typ = field["type"]
            if isinstance(typ, (list, tuple)):
                for typ in typ:
                    if typ is None:
                        continue
                    break
            format = field.get("format")
            return Pair(type=typ, format=format)
        except KeyError as e:
            logger.info("%s is not found. name=%s", e.args[0], name)
            if not field:
                return Pair(type="any", format=None)
            return Pair(type="object", format=None)

    def resolve_normalized_name(self, name: str) -> str:
        return normalize(name)

    def resolve_type_name(self, name: str) -> str:
        return titleize(name)

    def has_ref(self, d: AnyDict) -> bool:
        return "$ref" in d

    def get_ref(self, d: AnyDict) -> str:
        return d["$ref"]  # type: ignore

    def resolve_ref(self, ref: str) -> t.Tuple[str, AnyDict]:  # shallow
        # ref format is "#/components/schemas/<name>"
        # todo: cache
        path = ref[len("#/") :].split("/")
        name = path[-1]
        source = self._accessor.maybe_access(self.fulldata, path)
        return name, source

    def has_allof(self, d: AnyDict) -> bool:
        return "allOf" in d

    def has_array(self, d: AnyDict) -> bool:
        return d.get("type") == "array" or "items" in d

    def get_array_items(self, d: AnyDict) -> AnyDict:
        return d["items"]  # type: ignore

    def has_object(self, d: AnyDict, cand: t.Tuple[str, ...] = ("object",)) -> bool:
        typ = d.get("type", None)
        if typ in cand:
            return True
        if self.has_allof(d):
            return True
        return False

    def has_dict(self, d: AnyDict) -> bool:
        return "additionalProperties" in d and not (
            "properties" in d or "items" in d or "allOf" in d
        )

    def get_dict_addtional_properties(self, d: AnyDict) -> AnyDict:
        return d["additionalProperties"]  # type: ignore


class MetadataDict(tx.TypedDict, total=False):
    required: bool

    type: str
    format: str

    enum: str
    pattern: str


@dataclasses.dataclass
class Context:
    import_area: Module

    types: t.Dict[str, t.Union[Type, Container]] = dataclasses.field(
        default_factory=make_dict, repr=False
    )
    refs: t.Dict[str, Ref] = dataclasses.field(
        default_factory=make_dict, compare=False, repr=False
    )
    globals: t.Dict[str, t.Union[Repr, Type, Ref, Container]] = dataclasses.field(
        default_factory=make_dict, compare=False, repr=False
    )

    cache_counter: t.Counter[str] = dataclasses.field(
        default_factory=Counter, compare=False, repr=False
    )
    verbose: bool = False

    def apply_history(self, histories: t.List[t.Tuple[GUESS_KIND, str]]) -> None:
        itr = iter(reversed(histories))
        guess_kind, type_name = next(itr)
        typ = self.globals.get(type_name)

        if typ is None:
            assert guess_kind == "object", histories
            typ = self.types[type_name]
            self.globals[type_name] = typ

        for guess_kind, name in itr:
            if guess_kind == "?":
                continue

            prev_type = typ
            typ = self.globals.get(name)
            if guess_kind == "ref":
                if typ is not None:
                    if prev_type is not None:
                        assert typ == prev_type
                    continue
                if typ is None:
                    assert prev_type is not None
                    typ = self.globals[name] = prev_type
                continue
            elif guess_kind == "object":
                if typ is not None:
                    if prev_type is not None:
                        assert typ == prev_type
                    continue
                typ = self.globals[name] = self.types[name]
                assert typ == prev_type
                continue
            elif guess_kind == "array":
                if typ is not None:
                    if prev_type is not None:
                        assert len(typ.args) == 1  # type: ignore
                        assert typ.args[0] == prev_type  # type: ignore
                    continue
                typ = self.globals[name] = self.types[name] = List(prev_type)
                continue
            elif guess_kind == "dict":
                if typ is not None:
                    if prev_type is not None:
                        assert len(typ.args) == 2  # type:ignore
                        assert typ.args[1] == prev_type  # type:ignore
                    continue
                typ = self.globals[name] = self.types[name] = Dict(
                    Type(name="str"), prev_type
                )
                continue
            else:
                raise ValueError(f"unexpected guess kind {guess_kind}")


@dataclasses.dataclass(frozen=True)
class Repr:
    val: object
    metadata: MetadataDict = dataclasses.field(default_factory=make_dict)

    def as_type_str(self, ctx: Context) -> str:
        return repr(self.val)


@dataclasses.dataclass(frozen=True)
class Ref:
    ref: str
    inline: bool = False
    metadata: MetadataDict = dataclasses.field(default_factory=make_dict)

    @property
    def name(self) -> str:
        if self.inline:
            return self.ref
        return self.ref.rsplit("/", 1)[-1]

    def as_type_str(self, ctx: Context) -> str:
        name = self.name
        typ = ctx.globals.get(name)
        if typ is None:
            logger.info("as_type_str(): type %s is not found.", self.name)
            return f"TODO[{self.name}]"
        return typ.as_type_str(ctx)


@dataclasses.dataclass(frozen=True)
class Type:
    name: str
    bases: t.Tuple[str, ...] = dataclasses.field(default_factory=tuple)
    annotations: t.Dict[str, t.Union[Repr, Type, Ref, Container]] = dataclasses.field(
        default_factory=make_dict, compare=False, repr=False
    )
    module: str = ""
    metadata: MetadataDict = dataclasses.field(default_factory=make_dict)

    def as_type_str(self, ctx: Context) -> str:
        if not self.module:
            return self.name

        ctx.import_area.import_(self.module)
        return f"{self.module}.{self.name}"


@dataclasses.dataclass(frozen=True)
class Container:
    name: str
    module: str
    args: t.Sequence[t.Union[Repr, Type, Ref, Container]] = dataclasses.field(
        default_factory=list
    )
    metadata: MetadataDict = dataclasses.field(default_factory=make_dict)

    def as_type_str(self, ctx: Context) -> str:
        # TODO: cache
        args = [x.as_type_str(ctx) for x in self.args]
        fullname = self.module
        if self.module:
            ctx.import_area.import_(self.module)
            fullname = f"{self.module}.{self.name}"
        return f"{fullname}[{', '.join(args)}]"


def Optional(typ: t.Union[Repr, Type, Ref, Container]) -> Container:
    return Container(name="Optional", module="typing", args=[typ])


def List(typ: t.Union[Repr, Type, Ref, Container]) -> Container:
    return Container(name="List", module="typing", args=[typ])


def Literal(
    args: t.Sequence[Repr],
    *,
    module: str = "typing" if sys.version_info >= (3, 8) else "typing_extensions",
) -> Container:
    return Container(name="Literal", module=module, args=args)


def Dict(
    k: t.Union[Repr, Type, Ref, Container], v: t.Union[Repr, Type, Ref, Container]
) -> Container:
    return Container(name="Dict", module="typing", args=[k, v])


Pair = namedtuple("Pair", "type,format")

# TODO: correct mapping, https://swagger.io/specification/#format

TYPE_MAP = {
    Pair(type="integer", format=None): partial(Type, name="int"),
    Pair(type="integer", format="int32"): partial(Type, name="int"),
    Pair(type="number", format=None): partial(Type, name="float"),
    Pair(type="number", format="decimal"): partial(
        Type, name="Decimal", module="decimal",
    ),
    Pair(type="string", format=None): partial(Type, name="str"),
    Pair(type="boolean", format=None): partial(Type, name="bool"),
    Pair(type="string", format="uuid"): partial(Type, name="UUID", module="uuid"),
    Pair(type="string", format="date-time"): partial(
        Type, name="datetime", module="datetime",
    ),
    Pair(type="string", format="date"): partial(Type, name="date", module="datetime"),
    Pair(type="string", format="email"): partial(Type, name="string"),
    Pair(type="string", format="url"): partial(Type, name="string"),
}


class TypeGuesser:
    type_map = TYPE_MAP

    def __init__(
        self, *, type_map: t.Optional[t.Dict[Pair, partial[Type]]] = None,
    ):
        self.type_map = type_map or self.__class__.type_map
        self._unknown_type = Type(name="str", metadata={"format": "?"})

    def guess_type(self, pair: Pair, *, field: AnyDict) -> Type:
        factory = self.type_map.get(pair) or self.type_map.get(Pair(pair[0], None))
        if factory is None:
            return self._unknown_type
        return factory(metadata=field)


def scan(
    ctx: Context,
    *,
    d: AnyDict,
    items: t.Optional[t.Iterator[t.Tuple[str, AnyDict]]] = None,
) -> None:
    resolver = Resolver(d, refs=ctx.refs)

    q: t.Deque[
        t.Tuple[GUESS_KIND, str, AnyDict, t.List[t.Tuple[GUESS_KIND, str]]]
    ] = deque()
    a = Accessor(resolver, enqueue=q.appendleft)
    for name, sd in items or a.iterate_schemas(d):
        q.append(("?", name, sd, []))

    histories: t.List[t.List[t.Tuple[GUESS_KIND, str]]] = []
    cc = ctx.cache_counter
    try:
        while len(q) > 0:
            guess_kind, name, sd, history = q.popleft()
            # print("#", guess_kind, name, "--", history)
            history.append((guess_kind, name))
            if guess_kind == "?":
                if resolver.has_ref(sd):
                    q.appendleft(("ref", name, sd, history))
                elif resolver.has_array(sd):
                    q.appendleft(("array", name, sd, history))
                elif resolver.has_dict(sd):
                    q.appendleft(("dict", name, sd, history))
                elif resolver.has_object(sd):
                    q.appendleft(("object", name, sd, history))
                else:
                    q.appendleft(("primitive", name, sd, history))
                continue
            elif guess_kind == "ref":
                ref = resolver.get_ref(sd)
                ctx.refs[name] = Ref(ref=ref)
                new_name, new_sd = resolver.resolve_ref(ref)
                logger.debug("enqueue: ref %s as %s", name, new_name)
                q.appendleft(("?", new_name, new_sd, history))
                continue

            if name in cc:
                cc[name] += 1
                histories.append(history)
                continue
            cc[name] = 0

            if guess_kind == "array":
                logger.debug("enqueue: array item %s", name)
                new_sd = resolver.get_array_items(sd)
                q.appendleft(("?", name + "Item", new_sd, history))
                logger.debug("    use: array %s", name)
            elif guess_kind == "dict":
                logger.debug("enqueue: dict additionalProperties %s", name)
                new_sd = resolver.get_dict_addtional_properties(sd)
                q.appendleft(("?", name + "Map", new_sd, history))
                logger.debug("    use: dict %s", name)
            elif guess_kind == "object":
                logger.debug("    use: object %s", name)
                ctx.types[name] = a.extract_object_type(name, sd)
                ctx.apply_history(history)
            elif guess_kind == "primitive":
                logger.info("skip, primitive %r is skipped", name)
                ctx.globals[name] = resolver.resolve_type(sd, name=name)
                ctx.apply_history(history)  # todo:
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

    # import json
    # print(json.dumps(d, indent=2))

    # fix relation
    for h in histories:
        ctx.apply_history(h)


class Emitter:
    def __init__(self, *, m: t.Optional[Module] = None) -> None:
        self.m = m or Module()

    def emit(self, ctx: Context) -> Module:
        m = self.m
        for name, typ in ctx.types.items():
            if isinstance(typ, Container):
                logger.info("skip, emit %s", name)
                continue

            normalized_name = typ.name
            if name != normalized_name:
                m.stmt(f"# original is {name}")
            with m.class_(normalized_name):
                for field_name, field_type in typ.annotations.items():
                    metadata = field_type.metadata
                    if hasattr(field_type, "ref"):
                        field_type = ctx.globals.get(field_type.name)  # type: ignore
                        metadata.update(field_type.metadata)
                    if not metadata.get("required") or metadata.get("nullable"):
                        field_type = Optional(field_type)
                    type_str = field_type.as_type_str(ctx)
                    normalized_field_name = normalize(field_name)
                    if normalized_field_name == field_name:
                        m.stmt(f"{normalized_field_name}: {type_str}")
                    else:
                        m.stmt(
                            f"{normalized_field_name}: {type_str}  # original is {field_name}"
                        )
                    if ctx.verbose:
                        m.stmt(
                            "# metadata: {metadata}",
                            metadata=Repr(metadata).as_type_str(ctx),
                        )

        if str(ctx.import_area):
            ctx.import_area.sep()
        return m


def main(d: AnyDict, *, verbose: bool = False) -> None:
    logging.basicConfig(level=logging.INFO)  # debug

    m = Module()
    import_area: Module = m.submodule()
    import_area.stmt("from __future__ import annotations")

    ctx = Context(import_area=import_area, verbose=verbose)
    scan(ctx, d=d)

    emitter = Emitter(m=m)
    print(emitter.emit(ctx))

    cc = ctx.cache_counter
    logger.info("cache hits=%s, most common=%s", sum(cc.values()), cc.most_common(3))
