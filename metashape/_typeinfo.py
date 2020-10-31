from __future__ import annotations
import typing as t
from functools import partial
import dataclasses
import typing_extensions as tx


# TODO: support inheritance
# TODO: extract description
class _ForwardRef(tx.Protocol):
    @property
    def __forward_arg__(self) -> str:
        ...


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
    # if tx.Literal['x', 'y'] or t.NewType("X", str) -> [<new type>]
    supertypes: t.Tuple[t.Type[t.Any], ...] = dataclasses.field(repr=False, hash=False)

    # User -> User, int -> None, t.List[User] -> User
    # FIXME: t.Dict[User, User2] -> User  // ?? (User, User2) is needed?
    user_defined_type: t.Optional[t.Type[t.Any]] = dataclasses.field(
        default=None, hash=False
    )
    container_type: ContainerType = dataclasses.field(
        repr=True, hash=False, default="?"
    )
    is_newtype: bool = False


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
