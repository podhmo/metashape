from __future__ import annotations
import typing as t
from functools import partial
from functools import lru_cache
import dataclasses
import typing_extensions as tx
import typing_inspect


# TODO: support inheritance
# TODO: extract description

PrimitiveType = t.Union[int, bool, float, str, bytes]


def is_primitive_type(typ: t.Type[t.Any]) -> bool:
    return isinstance(typ, (bool, int, float, str, bytes))


ContainerType = tx.Literal["?", "list", "tuple", "dict", "set", "union"]


@dataclasses.dataclass(frozen=True)
class TypeInfo:
    raw: t.Type[t.Any]
    is_container: bool
    is_optional: bool
    is_combined: bool  # Union (for oneOf, anyOf, allOf)

    # t.Optional[X] -> X, t.List[X] -> t.List[X]
    type_: t.Type[t.Any] = dataclasses.field(repr=False, hash=False)

    # t.List[X] -> (X), t.Dict[K, V]-> (K, V)
    args: t.Tuple[TypeInfo, ...] = dataclasses.field(repr=False, hash=False)

    # tx.Literal['x', 'y'] -> str, t.Optional[tx.Literal['x', 'y']] -> str
    underlying: t.Type[t.Any] = dataclasses.field(repr=False, hash=False)
    # ?
    supertypes: t.Tuple[t.Type[t.Any], ...] = dataclasses.field(repr=False, hash=False)

    # User -> User, int -> None, t.List[User] -> User
    # FIXME: t.Dict[User, User2] -> User  // ?? (User, User2) is needed?
    user_defined_type: t.Optional[t.Type[t.Any]] = dataclasses.field(
        default=None, hash=False
    )
    container_type: ContainerType = dataclasses.field(
        repr=True, hash=False, default="?"
    )


Atom = partial(
    TypeInfo, is_optional=False, is_container=False, is_combined=False, args=(),
)

Container = partial(
    TypeInfo,
    is_optional=False,
    is_container=True,
    is_combined=False,
    underlying=type,
    supertypes=(),
    user_defined_type=None,
)


def Container_with_children(
    *,
    raw: t.Type[t.Any],
    type_: t.Type[t.Any],
    container_type: ContainerType,
    args: t.Tuple[TypeInfo, ...],
    is_optional: bool,
    is_combined: bool = False,
) -> TypeInfo:
    user_defined_type = None
    for childinfo in args:
        if childinfo.user_defined_type is not None:
            user_defined_type = childinfo.user_defined_type
            break

    # todo: collect all user defined type?
    return Container(
        raw=raw,
        type_=type_,
        container_type=container_type,
        args=args,
        is_optional=is_optional,
        is_combined=is_combined,
        user_defined_type=user_defined_type,
    )


def _default_raise_error(typ: t.Type[t.Any]) -> TypeInfo:
    raise ValueError(f"unsupported type {typ}")


# todo: rename
@lru_cache(maxsize=1024, typed=False)
def typeinfo(
    typ: t.Type[t.Any],
    *,
    is_optional: bool = False,
    user_defined_type: t.Optional[t.Type[t.Any]] = None,
    default: t.Callable[[t.Type[t.Any]], TypeInfo] = _default_raise_error,
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
            childinfo = typeinfo(_anytype, default=default)
            return Container(
                raw=raw,
                type_=tuple if issubclass(typ, tuple) else t.Sequence,
                container_type="tuple" if issubclass(typ, tuple) else "list",
                args=(childinfo,),
                user_defined_type=childinfo.user_defined_type,
            )
        elif issubclass(typ, t.Mapping):
            childinfo = typeinfo(_anytype, default=default)
            return Container(
                raw=raw,
                type_=t.Mapping,
                container_type="dict",
                args=(childinfo, childinfo),
                user_defined_type=childinfo.user_defined_type,
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
                    return Container_with_children(
                        container_type="union",
                        raw=raw,
                        type_=typ,
                        args=tuple([typeinfo(t, default=default) for t in args]),
                        is_optional=is_optional,
                        is_combined=True,
                    )
            else:
                is_optional = _nonetype in args
                if is_optional:
                    args = [x for x in args if x != _nonetype]
                    typ = t.Union[tuple(args)]
                return Container_with_children(
                    container_type="union",
                    raw=raw,
                    type_=typ,
                    args=tuple([typeinfo(t, default=default) for t in args]),
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
                return Container_with_children(
                    raw=raw,
                    type_=typ,
                    container_type="tuple" if issubclass(underlying, tuple) else "list",
                    args=tuple([typeinfo(t, default=default) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Mapping):
                args = typing_inspect.get_args(typ)
                return Container_with_children(
                    raw=raw,
                    type_=typ,
                    container_type="dict",
                    args=tuple([typeinfo(t, default=default) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Set):
                args = typing_inspect.get_args(typ)
                return Container_with_children(
                    raw=raw,
                    type_=typ,
                    container_type="set",
                    args=tuple([typeinfo(t, default=default) for t in args]),
                    is_optional=is_optional,
                )
            else:
                return default(typ)

    supertypes = []
    while hasattr(underlying, "__supertype__"):
        supertypes.append(underlying)  # todo: fullname?
        underlying = underlying.__supertype__

    if underlying not in _primitives:
        user_defined_type = underlying
    return Atom(
        raw=raw,
        type_=typ,
        underlying=underlying,
        is_optional=is_optional,
        user_defined_type=user_defined_type,
        supertypes=tuple(supertypes),
    )


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


if __name__ == "__main__":

    def main(argv: t.Optional[t.List[str]] = None) -> None:
        def run(path: str) -> None:
            from pprint import pprint
            from magicalimport import import_symbol

            x = import_symbol(path, cwd=True)
            pprint(typeinfo(x))

        import argparse

        parser = argparse.ArgumentParser(description=None)
        parser.print_usage = parser.print_help  # type: ignore
        parser.add_argument("path", help="<module>:<name>")
        args = parser.parse_args(argv)
        run(**vars(args))

    main()
