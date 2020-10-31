from __future__ import annotations
import typing as t
from ._typeinfo import (
    TypeInfo,
    _default_raise_error,
)

# HACK: supress mypy error with lru_cache, like below
#      error: Argument 1 to "__call__" of "_lru_cache_wrapper" has incompatible type "Type[Any]"; expected "Hashable"


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
    ...


def omit_optional(
    typ: t.Type[t.Any], *, _nonetype: t.Type[t.Any] = type(None)
) -> t.Tuple[t.Type[t.Any], bool]:
    ...
