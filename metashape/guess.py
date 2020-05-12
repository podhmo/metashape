import typing as t
import typing_extensions as tx
from collections import abc


def _titleize(name: str) -> str:
    if not name:
        return name
    name = str(name)
    return "{}{}".format(name[0].upper(), name[1:])


class NameGuesser:
    def __init__(
        self,
        *,
        formatter: t.Callable[[str], str] = _titleize,
        _aliases: t.Optional[t.Dict[object, str]] = None,
        _joiners: t.Optional[
            t.Dict[object, t.Callable[[t.Type[t.Any], t.Tuple[t.Any, ...]], str]]
        ] = None,
    ) -> None:
        self.format = formatter
        self._cache: t.Dict[int, str] = {}
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
        if hasattr(typ, "__name__"):
            py_clsname: str = getattr(typ, "__qualname__", typ.__name__)
            # HACK: for the type defined in closure. (e.g. t.NewType)
            if "<locals>" in py_clsname:
                py_clsname = typ.__name__
            return py_clsname

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


guess_name = NameGuesser().guess
