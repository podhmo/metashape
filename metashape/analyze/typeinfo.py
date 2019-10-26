from __future__ import annotations
import typing as t
from functools import lru_cache
import dataclasses
import typing_extensions as tx
import typing_inspect


# TODO: support inheritance
# TODO: extract description

ContainerType = tx.Literal["list", "tuple", "dict", "union"]


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class Container:
    raw: t.Type[t.Any]  # t.Optional[t.List[int]] -> t.Optional[t.List[int]]
    normalized: t.Type[t.Any]  # t.Optional[t.List[int]] -> t.List[int]
    container: ContainerType
    args: t.Tuple[TypeInfo, ...]

    is_optional: bool = False  # t.Optional[int] -> True, int -> False
    is_composite: bool = False  # t.Union -> True, dict -> False


@dataclasses.dataclass(frozen=True, unsafe_hash=False)
class Atom:
    raw: t.Type[t.Any]  # t.Optional[int] -> t.Optional[int]
    normalized: t.Type[
        t.Any
    ]  # t.Optional[tx.Literal["a", "b"]] -> tx.Literal["a", "b"]
    underlying: t.Type[t.Any]  # t.Optionall[tx.Literal["a", "b"]] -> str

    is_optional: bool = False  # t.Optional[int] -> True, int -> False
    custom: t.Optional[
        t.Type[t.Any]
    ] = None  # int -> None, Person -> Person, t.List[int] -> None
    supertypes: t.List[t.Type[t.Any]] = dataclasses.field(default_factory=list)


TypeInfo = t.Union[Atom, Container]


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


# TODO: move to method
def is_composite(info: TypeInfo) -> bool:
    # for performance (skip isinstance)
    return getattr(info, "is_composite", False)  # type: ignore


# TODO: move to method
def get_custom(info: TypeInfo) -> t.Optional[t.Type[t.Any]]:
    # for performance (skip isinstance)
    return getattr(info, "custom", None)  # type: ignore


# TODO: move to method
def get_args(info: TypeInfo) -> t.List[TypeInfo]:
    # for performance (skip isinstance)
    return getattr(info, "args", None) or []


# todo: rename
@lru_cache(maxsize=128, typed=False)
def typeinfo(
    typ: t.Type[t.Any],
    *,
    is_optional: bool = False,
    custom: t.Optional[t.Type[t.Any]] = None,
    _nonetype: t.Type[t.Any] = t.cast(t.Type[t.Any], type(None)),  # xxx
    _anytype: t.Type[t.Any] = t.cast(t.Type[t.Any], t.Any),  # xxx
    _primitives: t.Set[t.Type[t.Any]] = t.cast(
        t.Set[t.Type[t.Any]], set([str, int, bool, str, bytes, dict, list, t.Any])
    ),
) -> TypeInfo:
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
                        is_composite=True,
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
                    is_composite=True,
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
            else:
                raise ValueError(f"unsuported type %{typ}")

    supertypes = []
    while hasattr(underlying, "__supertype__"):
        supertypes.append(underlying)  # todo: fullname?
        underlying = underlying.__supertype__

    if underlying not in _primitives:
        custom = underlying
    return Atom(
        raw=raw,
        normalized=typ,
        underlying=underlying,
        is_optional=is_optional,
        custom=custom,
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
