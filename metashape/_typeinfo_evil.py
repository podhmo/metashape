from __future__ import annotations
import typing as t
import typing_extensions as tx
import dataclasses
from functools import lru_cache
from metashape.langhelpers import typing_get_args
from ._typeinfo import (
    TypeInfo,
    _default_raise_error,
    Container,
    Container_with_children,
    Atom,
)

_override_underlying_map = {}
try:
    from types import UnionType as Pep604Union

    _override_underlying_map[Pep604Union] = t.Union
except ImportError:
    pass  # py<3.10


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
        t.Set[t.Type[t.Any]],
        set([str, int, float, bool, str, bytes, dict, list, t.Any]),
    ),
) -> TypeInfo:
    raw = typ
    args: t.List[t.Type[t.Any]] = typing_get_args(typ)

    underlying = _override_underlying_map.get(typ.__class__)
    if underlying is None:
        underlying = getattr(typ, "__origin__", None)

    if underlying is None:
        if not hasattr(typ, "__iter__"):
            underlying = typ  # xxx
        elif issubclass(typ, str):
            underlying = typ
        elif issubclass(typ, bytes):
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
                    typ = t.Union[tuple(args)]  # type: ignore
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
                args = typing_get_args(typ)
                underlying = type(args[0])
            elif issubclass(underlying, t.Sequence):
                args = typing_get_args(typ)
                return Container_with_children(
                    raw=raw,
                    type_=typ,
                    container_type="tuple" if issubclass(underlying, tuple) else "list",
                    args=tuple([typeinfo(t, default=default) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Mapping):
                args = typing_get_args(typ)
                return Container_with_children(
                    raw=raw,
                    type_=typ,
                    container_type="dict",
                    args=tuple([typeinfo(t, default=default) for t in args]),
                    is_optional=is_optional,
                )
            elif issubclass(underlying, t.Set):
                args = typing_get_args(typ)
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

    if len(supertypes) > 0:
        underlying_info = typeinfo(underlying)
        return dataclasses.replace(
            underlying_info,
            is_newtype=True,
            supertypes=tuple(supertypes),
            raw=raw,
            type_=typ,
            is_optional=is_optional or underlying_info.is_optional,
        )

    if underlying not in _primitives:
        user_defined_type = underlying
    return Atom(
        raw=raw,
        type_=typ,
        underlying=underlying,
        is_optional=is_optional,
        user_defined_type=user_defined_type,
        supertypes=(),
        is_newtype=False,
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

    args = typing_get_args(typ)
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
    rtyp: t.Type[t.Any] = t.Union[tuple(args)]  # type:ignore
    return rtyp, True
