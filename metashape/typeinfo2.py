from __future__ import annotations
import typing as t
import dataclasses
from logging import getLogger

logger = getLogger(__name__)


@dataclasses.dataclass
class TypeInfo:
    # __slots__ = ("name", "underlying", "is_primitive", "is_container", "is_optional")

    name: str
    python_type: t.Type[t.Any]

    args: t.List[TypeInfo]
    underlying: TypeInfo  # for example, NewType[str] is passed, str is underlying type

    is_primitive: bool  # e.g. str, int is primitive
    is_container: bool = False  # array and dict are container (Union has args but not container?)
    is_optional: bool = False  # Nullable is is_optiiional

    is_enum: bool = False  #
    is_newtype: bool = False

    def __str__(self):
        newtype_suffix = "@" + self.underlying.name if self.is_newtype else ""
        optional_suffix = "?" if self.is_optional else ""
        return (
            f"{self.__class__.__name__}[{self.name}{newtype_suffix}{optional_suffix}]"
        )


_nonetype: t.Type[t.Any] = t.cast(t.Type[t.Any], type(None))  # xxx
_anytype: t.Type[t.Any] = t.cast(t.Type[t.Any], t.Any)  # xxx
_primitives_types: t.Set[t.Type[t.Any]] = set(
    [str, int, float, bool, str, bytes, dict, list, t.Any]
)

_zero = TypeInfo(name="*zero*", python_type=TypeInfo, args=[], underlying=None, is_primitive=True)  # type: ignore
_zero = dataclasses.replace(_zero, underlying=_zero)


# TODO: t.List[str]
# TODO: user defined class
# TODO: t.Literal["A","B", "C"]


# TODO: cache
def typeinfo(typ: t.Type[t.Any], _toplevel: bool = True) -> TypeInfo:
    if _toplevel:
        logger.debug("-------------------- typeinfo: %r --------------------", typ)
    ti = _typeinfo(typ, raw=typ, is_optional=False, lv=0)
    if _toplevel:
        logger.debug("-- %r --", ti)
    return ti


def _typeinfo(
    typ: t.Type[t.Any],
    *,
    raw: t.Type[t.Any],
    underlying: TypeInfo = _zero,
    is_optional: bool = False,
    is_newtype: bool = False,
    lv: int = 0,
) -> TypeInfo:
    logger.debug("\t%s%r", "  " * lv, typ)
    args = getattr(typ, "__args__", None) or []
    origin = getattr(typ, "__origin__", None)

    supertypes = []
    while hasattr(typ, "__supertype__"):
        supertypes.append(typ)  # todo: fullname?
        typ = typ.__supertype__
        is_newtype = True

    if origin is None:
        python_type = typ
        underlying = _zero
        if is_newtype:
            python_type = raw
            underlying = typeinfo(typ, _toplevel=False)
        return dataclasses.replace(
            _zero,
            name=python_type.__name__,
            underlying=underlying,
            python_type=python_type,
            is_newtype=is_newtype,
            is_optional=is_optional,
        )

    if origin == t.Union:
        if len(args) == 2:
            if args[0] == _nonetype:
                typ = args[1]
                return _typeinfo(
                    typ,
                    raw=typ,
                    is_newtype=is_newtype,
                    is_optional=True,
                    lv=lv + 1,
                )
            elif args[1] == _nonetype:
                typ = args[0]
                return _typeinfo(
                    typ,
                    raw=typ,
                    is_newtype=is_newtype,
                    is_optional=True,
                    lv=lv + 1,
                )
        is_optional = _nonetype in args
        if is_optional:
            args = [x for x in args if x != _nonetype]
        typ = t.Union[tuple(sorted(args, key=str))]  # type: ignore
        return TypeInfo(
            name=str(typ),
            python_type=typ,
            underlying=_zero,  # xxx?
            args=[typeinfo(x, _toplevel=False) for x in args],
            is_optional=is_optional,
            is_primitive=False,
        )

    raise NotImplementedError("never")


def fullname(o):
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__
    return module + "." + o.__class__.__name__


if __name__ == "__main__":
    import logging
    import os

    if bool(int(os.getenv("DEBUG") or "0")):
        logging.basicConfig(level=logging.DEBUG)

    print("\t** int", "->", typeinfo(int))
    print("\t** str", "->", typeinfo(str))
    print("")

    # optional
    print("\t** t.Optional[str]", "->", typeinfo(t.Optional[str]))
    print("\t** t.Union[str, None]", "->", typeinfo(t.Union[str, None]))
    print("\t** t.Union[None, str]", "->", typeinfo(t.Union[None, str]))
    print("")

    # union
    print("\t** t.Union[int, str]", "->", typeinfo(t.Union[int, str]))
    print(
        "\t** t.Union[str, int]", "->", typeinfo(t.Union[str, int])
    )  # sorted: int, str
    print(
        "\t** t.Union[str, int, None]", "->", typeinfo(t.Union[str, int, None])
    )  # sorted: int, str
    print("")

    # new type
    Name = t.NewType("Name", str)
    print("\t** t.NewType('Name', str)", "->", typeinfo(Name))
    print("\t** t.Optional[t.NewType('Name', str)]]", "->", typeinfo(t.Optional[Name]))
    Name2 = t.NewType("Name2", Name)
    print("\t** t.NewType('Name2', str)", "->", typeinfo(Name2))
    print(
        "\t** t.Optional[t.NewType('Name2', str)]]", "->", typeinfo(t.Optional[Name2])
    )
    print("")

    # user defined class
    # TODO: fullpath
    class A:
        pass

    class B:
        pass

    print("\t** A", "->", typeinfo(A))
    print("\t** B", "->", typeinfo(B))
