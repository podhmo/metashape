from __future__ import annotations
import typing as t
from functools import lru_cache
import typing_extensions as tx
import typing_inspect


# TODO: support inheritance
# TODO: extract description

ContainerType = tx.Literal["list", "tuple", "dict", "union"]


class Container(tx.TypedDict, total=True):
    raw: t.Type[t.Any]  # t.Optional[t.List[int]] -> t.Optional[t.List[int]]
    container: ContainerType
    args: t.Tuple[TypeInfo, ...]

    is_optional: bool  # t.Optional[int] -> True, int -> False
    is_composite: bool  # t.Union -> True, dict -> False


class Atom(tx.TypedDict, total=True):
    raw: t.Type[t.Any]  # t.Optional[int] -> t.Optional[int]
    underlying: t.Type[t.Any]  # t.Optionall[int] -> int

    is_optional: bool  # t.Optional[int] -> True, int -> False
    custom: t.Optional[
        t.Type[t.Any]
    ]  # int -> None, Person -> Person, t.List[int] -> None


TypeInfo = t.Union[Atom, Container]


def _make_atom(
    *,
    raw: t.Type[t.Any],
    underlying: t.Type[t.Any],
    is_optional: bool = False,
    custom: t.Optional[t.Any] = None,
) -> Atom:
    return {
        "raw": raw,
        "underlying": underlying,
        "is_optional": is_optional,
        "custom": custom,
    }


def _make_container(
    *,
    container: ContainerType,
    raw: t.Type[t.Any],
    args: t.Tuple["TypeInfo", ...],
    is_optional: bool = False,
    is_composite: bool = False,
) -> Container:
    return {
        "raw": raw,
        "args": tuple(args),
        "container": container,
        "is_optional": is_optional,
        "is_composite": is_composite,
    }


@lru_cache(maxsize=128, typed=False)
def detect(
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
            return _make_container(
                raw=raw,
                container="tuple" if issubclass(typ, tuple) else "list",
                args=(detect(_anytype),),
            )
        elif issubclass(typ, t.Mapping):
            childinfo = detect(_anytype)
            return _make_container(
                raw=raw, container="dict", args=(childinfo, childinfo)
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
                    return _make_container(
                        container="union",
                        raw=raw,
                        args=tuple([detect(t) for t in args]),
                        is_optional=is_optional,
                        is_composite=True,
                    )
            else:
                is_optional = _nonetype in args
                if is_optional:
                    args = [x for x in args if x != _nonetype]
                return _make_container(
                    container="union",
                    raw=raw,
                    args=tuple([detect(t) for t in args]),
                    is_optional=is_optional,
                    is_composite=True,
                )

        if hasattr(typ, "__origin__"):
            underlying = typ.__origin__
            if underlying == tx.Literal:
                args = typing_inspect.get_args(typ)
                underlying = type(args[0])  # TODO: meta info
            elif issubclass(underlying, t.Sequence):
                args = typing_inspect.get_args(typ)
                return _make_container(
                    raw=raw,
                    container="tuple" if issubclass(underlying, tuple) else "list",
                    args=tuple([detect(t) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Mapping):
                args = typing_inspect.get_args(typ)
                return _make_container(
                    raw=raw,
                    container="dict",
                    args=tuple([detect(t) for t in args]),
                    is_optional=is_optional,
                )
            else:
                raise ValueError(f"unsuported type %{typ}")

    while hasattr(underlying, "__supertype__"):
        underlying = underlying.__supertype__

    if underlying not in _primitives:
        custom = underlying
    return _make_atom(
        raw=raw, underlying=underlying, is_optional=is_optional, custom=custom
    )


if __name__ == "__main__":

    def main(argv: t.Optional[t.List[str]] = None) -> None:
        def run(path: str) -> None:
            from pprint import pprint
            from magicalimport import import_symbol

            x = import_symbol(path)
            pprint(detect(x))

        import argparse

        parser = argparse.ArgumentParser(description=None)
        parser.print_usage = parser.print_help  # type: ignore
        parser.add_argument("path", help="<module>:<name>")
        args = parser.parse_args(argv)
        run(**vars(args))

    main()
