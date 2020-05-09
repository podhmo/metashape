from __future__ import annotations
import typing as t
from functools import lru_cache
import dataclasses
import typing_extensions as tx
import typing_inspect


# TODO: support inheritance
# TODO: extract description

PrimitiveType = t.Union[int, bool, float, str, bytes]


def is_primitive_type(typ: t.Type[t.Any]) -> bool:
    return isinstance(typ, (bool, int, float, str, bytes))


ContainerType = tx.Literal["list", "tuple", "dict", "set", "union"]


@dataclasses.dataclass(frozen=True, unsafe_hash=True, repr=False)
class TypeInfo:
    is_container: bool
    is_optional: bool
    is_combined: bool  # Union (for oneOf, anyOf, allOf)

    raw: t.Type[t.Any]
    normalized: t.Type[t.Any]
    args: t.Tuple[TypeInfo, ...]

    underlying: t.Type[t.Any]
    supertypes: t.Tuple[t.Type[t.Any], ...]

    user_defined_type: t.Optional[t.Type[t.Any]] = None  # todo:rename

    _atom: t.Optional[Atom] = None
    _container: t.Optional[Container] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.raw}>"

    @property
    def atom(self) -> Atom:
        assert self._atom is not None
        return self._atom

    @property
    def container(self) -> Container:
        assert self._container is not None
        return self._container


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class Container:
    raw: t.Type[t.Any]  # t.Optional[t.List[int]] -> t.Optional[t.List[int]]
    normalized: t.Type[t.Any]  # t.Optional[t.List[int]] -> t.List[int]
    container: ContainerType
    args: t.Tuple[TypeInfo, ...]

    is_optional: bool = False  # t.Optional[int] -> True, int -> False
    is_combined: bool = False  # t.Union -> True, dict -> False


@dataclasses.dataclass(frozen=True, unsafe_hash=False)
class Atom:
    raw: t.Type[t.Any]  # t.Optional[int] -> t.Optional[int]
    normalized: t.Type[
        t.Any
    ]  # t.Optional[tx.Literal["a", "b"]] -> tx.Literal["a", "b"]
    underlying: t.Type[t.Any]  # t.Optionall[tx.Literal["a", "b"]] -> str

    is_optional: bool = False  # t.Optional[int] -> True, int -> False

    supertypes: t.List[t.Type[t.Any]] = dataclasses.field(default_factory=list)

    # int -> None, Person -> Person, t.List[int] -> None
    # FIXME: support  t.List[Person] -> Person
    user_defined_type: t.Optional[t.Type[t.Any]] = None


_TypeInfoCandidate = t.Union[Atom, Container]


@lru_cache(maxsize=128, typed=False)
def omit_optional(
    typ: t.Type[t.Any], *, _nonetype: t.Type[t.Any] = type(None)
) -> t.Tuple[t.Type[t.Any], bool]:
    origin = getattr(typ, "__origin__", None)
    if origin is None:
        return typ, False
    if origin != t.Union:
        return typ, False

    args = typing_inspect.get_args(typ)
    if len(args) == 2:
        if args[0] == _nonetype:
            return args[1], True
        elif args[1] == _nonetype:
            return args[0], True
        else:
            return typ, False

    is_optional = _nonetype in args
    if not is_optional:
        return typ, False
    args = [x for x in args if x != _nonetype]
    return t.Union[tuple(args)], True


def _from_atom(c: Atom) -> TypeInfo:
    return TypeInfo(
        is_optional=c.is_optional,
        is_container=False,
        is_combined=False,
        raw=c.raw,
        normalized=c.normalized,
        underlying=c.underlying,
        args=(),
        supertypes=tuple(c.supertypes),
        user_defined_type=c.user_defined_type,
        _atom=c,
    )


def _from_container(c: Container) -> TypeInfo:
    return TypeInfo(
        is_optional=c.is_optional,
        is_container=True,
        is_combined=c.is_combined,
        raw=c.raw,
        normalized=c.normalized,
        underlying=type,  # xxx
        args=tuple(c.args),
        supertypes=(),
        user_defined_type=None,
        _container=c,
    )


@lru_cache(maxsize=1024, typed=False)
def typeinfo(typ: t.Type[t.Any]) -> TypeInfo:
    c = _typeinfo(typ)
    if isinstance(c, Atom):
        return _from_atom(c)
    else:
        return _from_container(c)


def _typeinfo(
    typ: t.Type[t.Any],
    *,
    is_optional: bool = False,
    user_defined_type: t.Optional[t.Type[t.Any]] = None,
    _nonetype: t.Type[t.Any] = t.cast(t.Type[t.Any], type(None)),  # xxx
    _anytype: t.Type[t.Any] = t.cast(t.Type[t.Any], t.Any),  # xxx
    _primitives: t.Set[t.Type[t.Any]] = t.cast(
        t.Set[t.Type[t.Any]], set([str, int, bool, str, bytes, dict, list, t.Any])
    ),
) -> _TypeInfoCandidate:
    raw = typ
    args = typing_inspect.get_args(typ)
    underlying = getattr(typ, "__origin__", None)

    if underlying is None:
        if not hasattr(typ, "__iter__"):
            underlying = typ  # xxx
        elif issubclass(typ, str):
            underlying = typ
        elif issubclass(typ, t.Sequence):
            return Container(
                raw=raw,
                normalized=tuple if issubclass(typ, tuple) else t.Sequence,
                container="tuple" if issubclass(typ, tuple) else "list",
                args=(typeinfo(_anytype),),
            )
        elif issubclass(typ, t.Mapping):
            childinfo = typeinfo(_anytype)
            return Container(
                raw=raw,
                normalized=t.Mapping,
                container="dict",
                args=(childinfo, childinfo),
            )
        else:
            underlying = typ  # xxx
    else:
        if underlying == t.Union:
            if len(args) == 2:
                if args[0] == _nonetype:
                    is_optional = True
                    typ = underlying = args[1]
                elif args[1] == _nonetype:
                    is_optional = True
                    typ = underlying = args[0]
                else:
                    return Container(
                        container="union",
                        raw=raw,
                        normalized=typ,
                        args=tuple([typeinfo(t) for t in args]),
                        is_optional=is_optional,
                        is_combined=True,
                    )
            else:
                is_optional = _nonetype in args
                if is_optional:
                    args = [x for x in args if x != _nonetype]
                    typ = t.Union[tuple(args)]
                return Container(
                    container="union",
                    raw=raw,
                    normalized=typ,
                    args=tuple([typeinfo(t) for t in args]),
                    is_optional=is_optional,
                    is_combined=True,
                )

        if hasattr(typ, "__origin__"):
            underlying = typ.__origin__
            if underlying == tx.Literal:
                args = typing_inspect.get_args(typ)
                underlying = type(args[0])
            elif issubclass(underlying, t.Sequence):
                args = typing_inspect.get_args(typ)
                return Container(
                    raw=raw,
                    normalized=typ,
                    container="tuple" if issubclass(underlying, tuple) else "list",
                    args=tuple([typeinfo(t) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Mapping):
                args = typing_inspect.get_args(typ)
                return Container(
                    raw=raw,
                    normalized=typ,
                    container="dict",
                    args=tuple([typeinfo(t) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Set):
                args = typing_inspect.get_args(typ)
                return Container(
                    raw=raw,
                    normalized=typ,
                    container="set",
                    args=tuple([typeinfo(t) for t in args]),
                    is_optional=is_optional,
                )
            else:
                raise ValueError(f"unsuported type %{typ}")

    supertypes = []
    while hasattr(underlying, "__supertype__"):
        supertypes.append(underlying)  # todo: fullname?
        underlying = underlying.__supertype__

    if underlying not in _primitives:
        user_defined_type = underlying
    return Atom(
        raw=raw,
        normalized=typ,
        underlying=underlying,
        is_optional=is_optional,
        user_defined_type=user_defined_type,
        supertypes=supertypes,
    )


if __name__ == "__main__":

    def main(argv: t.Optional[t.List[str]] = None) -> None:
        def run(path: str) -> None:
            from pprint import pprint
            from magicalimport import import_symbol

            x = import_symbol(path)
            pprint(typeinfo(x))

        import argparse

        parser = argparse.ArgumentParser(description=None)
        parser.print_usage = parser.print_help  # type: ignore
        parser.add_argument("path", help="<module>:<name>")
        args = parser.parse_args(argv)
        run(**vars(args))

    main()
