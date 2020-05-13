import typing as t
import typing_extensions as tx
import weakref
from collections import abc


TypeT = t.TypeVar("TypeT", bound=type)


class _Fake:
    def __init__(self, name: str) -> None:
        self.name = name


_ELLIPSIS = _Fake("...")


class NameResolver:
    def __init__(self) -> None:
        self.pool: weakref.WeakKeyDictionary[str] = weakref.WeakKeyDictionary()
        self.indirect_map: weakref.WeakValueDictionary[
            t.Tuple[t.Any, ...]
        ] = weakref.WeakValueDictionary()

    def _get_key(self, typ: TypeT) -> object:
        if typ is ...:
            return _ELLIPSIS
        return typ

    def register(self, name: str, typ: TypeT) -> TypeT:
        k = self._get_key(typ)
        self.pool[k] = name
        if hasattr(typ, "__args__"):
            self.indirect_map[self._get_indirect_key(typ)] = k
        return typ

    def _get_indirect_key(self, typ: t.Type[t.Any]) -> t.Tuple[t.Any, ...]:
        return tuple([typ.__origin__, *sorted([str(x) for x in typ.__args__]),],)

    def resolve_maybe(self, typ: TypeT) -> t.Optional[str]:
        name = self.pool.get(self._get_key(typ))
        if name is not None:
            return name

        if hasattr(typ, "__name__"):
            name = getattr(typ, "__qualname__", typ.__name__)
            # HACK: for the type defined in closure. (e.g. t.NewType)
            if "<locals>" in name:
                name = typ.__name__
            return name
        elif hasattr(typ, "__args__"):
            ik = self._get_indirect_key(typ)
            k = self.indirect_map.get(ik)
            if k is not None:
                name = self.pool.get(k)
                if name is not None:
                    self.pool[self._get_key(typ)] = name
                    return name
        return None

    def resolve(self, typ: TypeT) -> str:
        name = self.resolve_maybe(typ)
        if name is not None:
            return name
        raise RuntimeError(
            "this type is not named, please considering use NewNamedType(<name>, <type>)"
        )


def _titleize(name: str) -> str:
    if not name:
        return name
    name = str(name)
    return "{}{}".format(name[0].upper(), name[1:])


class NameGuesser:
    def __init__(
        self,
        resolver: NameResolver,
        *,
        formatter: t.Callable[[str], str] = _titleize,
        _aliases: t.Optional[t.Dict[object, str]] = None,
        _joiners: t.Optional[
            t.Dict[object, t.Callable[[t.Type[t.Any], t.Tuple[t.Any, ...]], str]]
        ] = None,
    ) -> None:
        self.resolver = resolver
        self.format = formatter
        self._cache: t.Dict[int, str] = {}  # leak
        self._aliases = _aliases or {...: "N", t.Any: "Any"}
        self._joiners = _joiners or {
            t.Any: self._join_name_for_default,
            t.Union: self._join_name_for_union,
            abc.Callable: self._join_name_for_callable,
            t.Callable: self._join_name_for_callable,
            tx.Literal: self._join_name_for_literal,
        }
        assert t.Any in self._joiners

    def guess(self, typ: t.Type[t.Any]) -> str:
        cached = self._cache.get(id(typ))
        if cached is not None:
            return cached
        guessed = self._guess(typ)
        self._cache[id(typ)] = guessed
        return guessed

    def _guess(self, typ: t.Type[t.Any]) -> str:
        name = self.resolver.resolve_maybe(typ)
        if name is not None:
            return name

        alias = self._aliases.get(typ)
        if alias is not None:
            return alias

        # for generics
        origin = typ.__origin__
        joiner = self._joiners.get(origin) or self._joiners[t.Any]
        return joiner(origin, typ.__args__)

    def _join_name_for_default(
        self, origin: t.Type[t.Any], args: t.Tuple[t.Type[t.Any], ...],
    ) -> str:
        subtypes: t.List[t.Type[t.Any]] = []
        subtypes.extend(args)
        subtypes.append(origin)
        sep = ""
        return sep.join([self.format(self.guess(subtype)) for subtype in subtypes])

    def _join_name_for_union(
        self, origin: t.Type[t.Any], args: t.Tuple[t.Type[t.Any], ...],
    ) -> str:
        subtypes: t.List[t.Type[t.Any]] = []
        subtypes.extend(args)
        sep = "or"
        return sep.join(
            sorted([self.format(self.guess(subtype)) for subtype in subtypes])
        )

    def _join_name_for_callable(
        self, origin: t.Type[t.Any], args: t.Tuple[t.Type[t.Any], ...],
    ) -> str:
        assert len(args) == 2
        prefix = self.format(self.guess(args[0]))
        suffix = ""
        if args[1]:
            suffix = f"Return{self.format(self.guess(args[1]))}"
        return f"{prefix}{suffix}Callable"

    def _join_name_for_literal(
        self, origin: t.Type[t.Any], args: t.Tuple[t.Type[t.Any], ...],
    ) -> str:
        elements = t.cast(t.List[str], args)
        return "or".join([self.format(e) for e in elements])


_resolver = NameResolver()
_guesser = NameGuesser(_resolver)


def NewNamedType(
    name: str, typ: TypeT, *, _resolver: NameResolver = _resolver
) -> TypeT:
    _resolver.register(name, typ)
    return typ


guess_name = _guesser.guess
resolve = _resolver.resolve
resolve_maybe = _resolver.resolve_maybe
