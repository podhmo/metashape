from __future__ import annotations
import typing as t
import dataclasses
from logging import getLogger


logger = getLogger(__name__)


# TODO: fullname


@dataclasses.dataclass(slots=True, frozen=True)
class TypeInfo:
    """
    str                  -> is_primitive=True
    NewType("Name", str) -> is_primitive=True, is_newtype=True
    Literal["x","y","z"] -> is_primitive=True, is_newtype=True?, is_enum=True
    List[str]            -> is_primitive=False, is_container=True, args=[TypeInfo[str]], python_container_type=list
    Union[int, str]      -> is_primitive=False, is_container=True?, args=[TypeInfo[int], TypeInfo[str]]
    Union[str, int]      -> is_primitive=False, is_container=True?, args=[TypeInfo[int], TypeInfo[str]]  # sorted

    class A: pass
    class B: pass

    A                    -> is_primitive=False, named_members=[TypeInfo[A]]
    NewType("A", B)      -> is_primitive=False, named_members=[TypeInfo[A]], is_newtype=True
    List[A]              -> is_primitive=False, named_members=[TypeInfo[A]], is_container=True, python_container_type=list
    Dict[A, B]           -> is_primitive=False, named_members=[TypeInfo[A], TypeInfo[B]], is_container=True, python_container_type=dict
    """

    name: str
    python_type: t.Type[t.Any]
    args: t.List[TypeInfo]
    named_members: t.List[TypeInfo]  # todo: renmae
    enum_values: t.Tuple[t.Any, ...]

    _underlying: t.Optional[
        TypeInfo
    ] = None  # for example, NewType[str] is passed, str is underlying type
    python_container_type: t.Optional[t.Type[t.Any]] = None
    is_optional: bool = False  # Nullable

    @property
    def underlying(self) -> TypeInfo:
        underlying = self
        while underlying._underlying is not None:
            underlying = underlying._underlying
        return underlying

    @property
    def is_primitive(self) -> bool:
        # e.g. str, int is primitive
        return not (
            self._underlying is not None or len(self.named_members) > 0
        )

    @property
    def is_enum(self) -> bool:
        return len(self.enum_values) > 0

    @property
    def is_newtype(self) -> bool:
        return self._underlying is not None

    @property
    def is_container(self) -> bool:
        # array and dict are container (Union has args but not container?)
        return self.python_container_class is not None

    @property
    def has_named_members(self) -> bool:
        return len(self.named_members) > 0

    def __str__(self):
        named_members_suffix = (
            "#" + ",".join(x.name for x in self.named_members)
            if len(self.named_members) > 0
            else ""
        )
        newtype_suffix = "@" + self.underlying.name if self.is_newtype else ""
        optional_suffix = "?" if self.is_optional else ""
        return f"{self.__class__.__name__}[{self.name}{named_members_suffix}{newtype_suffix}{optional_suffix}]"


_nonetype: t.Type[t.Any] = t.cast(t.Type[t.Any], type(None))  # xxx
_anytype: t.Type[t.Any] = t.cast(t.Type[t.Any], t.Any)  # xxx
_primitives_types: t.Set[t.Type[t.Any]] = set(
    [str, int, float, bool, str, bytes, dict, list, t.Any]
)


# TODO: t.List[str]
# TODO: user defined class
# TODO: t.Literal["A","B", "C"]


# TODO: cache
def typeinfo(typ: t.Type[t.Any], _toplevel: bool = True, lv: int = 0) -> TypeInfo:
    if _toplevel:
        logger.debug("-------------------- typeinfo: %r --------------------", typ)
    ti = _typeinfo(typ, is_optional=False, lv=lv)
    if _toplevel:
        logger.debug("-- %r --", ti)
    return ti


def _typeinfo(
    typ: t.Type[t.Any],
    *,
    underlying: t.Optional[TypeInfo] = None,
    is_optional: bool = False,
    lv: int = 0,
) -> TypeInfo:
    logger.debug("\t%s%r", "  " * lv, typ)
    args = getattr(typ, "__args__", None) or []
    origin = getattr(typ, "__origin__", None)

    supertypes = []
    raw_type = typ
    while hasattr(typ, "__supertype__"):
        supertypes.append(typ)  # todo: fullname?
        typ = typ.__supertype__
    is_newtype = raw_type != typ

    if origin is None:  # for NewType
        python_type = typ
        args = []
        enum_values = ()
        named_members = []
        if is_newtype:
            python_type = raw_type
            underlying = typeinfo(typ, _toplevel=False, lv=lv + 1)
            args = underlying.args
            enum_values = underlying.enum_values
            named_members = underlying.named_members[:]

        ti = TypeInfo(
            name=python_type.__name__,
            python_type=python_type,
            args=args,
            enum_values=enum_values,
            named_members=named_members,
            _underlying=underlying,
            is_optional=is_optional,
        )
        if python_type not in _primitives_types:
            named_members.append(ti)
        return ti
    elif origin == t.Union:
        if len(args) == 2:
            if args[0] == _nonetype:
                return _typeinfo(
                    args[1],
                    is_optional=True,
                    lv=lv + 1,
                )
            elif args[1] == _nonetype:
                return _typeinfo(
                    args[0],
                    is_optional=True,
                    lv=lv + 1,
                )

        new_args = sorted([x for x in args if x != _nonetype], key=str)
        typ = t.Union[tuple(new_args)]  # type: ignore
        args_info_list = [typeinfo(x, _toplevel=False, lv=lv + 1) for x in new_args]
        return TypeInfo(
            name=str(typ),
            python_type=typ,
            python_container_type=t.Union,
            args=args_info_list,
            enum_values=(),
            named_members=[
                ut for x in args_info_list for ut in x.named_members
            ],  # TODO: dedup
            is_optional=len(args) != len(new_args),
        )
    elif origin == t.Literal:
        enum_values = t.get_args(typ)
        underlying = typeinfo(type(enum_values[0]), _toplevel=False, lv=lv + 1)
        return TypeInfo(
            name=str(typ),
            python_type=typ,
            python_container_type=t.Literal,
            args=[],
            enum_values=enum_values,
            named_members=[],
            _underlying=underlying,
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

    # literal
    Direction = t.Literal["up", "down", "left", "right"]
    print('\t** t.Literal["up", "down", "left", "right"]', "->", typeinfo(Direction))
    Direction2 = t.NewType("Direction2", Direction)
    print('\t** t.NewType("Direction2", t.Literal["up", "down", "left", "right"])', "->", typeinfo(Direction2))
    print(typeinfo(Direction).enum_values)
    print(typeinfo(Direction2).enum_values)
    print("")

    # user defined class
    # TODO: fullpath
    class A:
        pass

    class B:
        pass

    print("\t** A", "->", typeinfo(A))
    print("\t** B", "->", typeinfo(B))
