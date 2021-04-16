# type: ignore
from __future__ import annotations
import typing as t
import sys
import dataclasses
import typing_extensions as tx
import pytest


_MyString = t.NewType("_MyString", str)
_MyString2 = t.NewType("_MyString2", _MyString)
_Optional_MyString = t.NewType("_Optional_MyString", t.Optional[_MyString])


class _Person:
    name: str


_MyPerson = t.NewType("_MyPerson", _Person)
_MyPeople = t.NewType("_MyPeople", t.List[_MyPerson])


def atom(
    *,
    raw,
    underlying=None,
    type_=None,
    is_optional=False,
    user_defined_type=None,
    supertypes=None
):
    from metashape.typeinfo import Atom

    return Atom(
        raw=raw,
        underlying=underlying or raw,
        type_=type_ or raw or underlying,
        is_optional=is_optional,
        user_defined_type=user_defined_type,
        supertypes=tuple(supertypes or ()),
        is_newtype=len(supertypes or []) > 0,
    )


def container(
    *,
    container_type,
    raw,
    type_=None,
    is_optional=False,
    is_combined=False,
    raw_args=None,
    args=None,
    supertypes=None
):
    from metashape.typeinfo import Container_with_children

    raw_args = raw_args or [atom(raw=x, underlying=x) for x in args]
    info = Container_with_children(
        raw=raw,
        type_=type_ or raw,
        args=tuple(raw_args),
        container_type=container_type,
        is_optional=is_optional,
        is_combined=is_combined,
    )
    if supertypes:
        info = dataclasses.replace(
            info,
            supertypes=tuple(supertypes or ()),
            is_newtype=len(supertypes or []) > 0,
        )
    return info


@pytest.mark.parametrize(
    "typ, want, omitted",
    [
        (int, int, False),
        (t.Optional[int], int, True),
        (t.Union[int, str], t.Union[int, str], False),
        (t.Union[int, t.Optional[str]], t.Union[int, str], True),
        (t.List[int], t.List[int], False),
        (t.List[t.Optional[int]], t.List[t.Optional[int]], False),
    ],
)
def test_omit_optional(typ, want, omitted):
    from metashape.typeinfo import omit_optional as callFUT

    got = callFUT(typ)
    assert got == (want, omitted)


py39List = list
if sys.version_info < (3, 9):
    py39List = t.List


@pytest.mark.parametrize(
    "msg, typ, want",
    [
        ("atom int", int, atom(raw=int, underlying=int)),
        ("atom str", str, atom(raw=str, underlying=str)),
        (
            "atom optional str",
            t.Optional[str],
            atom(raw=t.Optional[str], type_=str, underlying=str, is_optional=True),
        ),
        # container
        (
            "list str",
            t.List[str],
            container(raw=t.List[str], container_type="list", args=[str]),
        ),
        (
            "list str",
            py39List[str],
            container(raw=py39List[str], container_type="list", args=[str]),
        ),
        (
            "optional list str",
            t.Optional[t.List[str]],
            container(
                raw=t.Optional[t.List[str]],
                type_=t.List[str],
                container_type="list",
                args=[str],
                is_optional=True,
            ),
        ),
        (
            "list optional str",
            t.List[t.Optional[str]],
            container(
                raw=t.List[t.Optional[str]],
                container_type="list",
                raw_args=[
                    atom(
                        raw=t.Optional[str],
                        type_=str,
                        underlying=str,
                        is_optional=True,
                    )
                ],
            ),
        ),
        (
            "list t.Any",
            list,
            container(raw=list, type_=t.Sequence, container_type="list", args=[t.Any]),
        ),
        (
            "tuple str",
            t.Tuple[str],
            container(raw=t.Tuple[str], container_type="tuple", args=[str]),
        ),
        (
            "tuple2 str int",
            t.Tuple[str, int],
            container(raw=t.Tuple[str, int], container_type="tuple", args=[str, int]),
        ),
        (
            "dict str int",
            t.Dict[str, int],
            container(raw=t.Dict[str, int], container_type="dict", args=[str, int]),
        ),
        (
            "optional dict str int",
            t.Optional[t.Dict[str, int]],
            container(
                raw=t.Optional[t.Dict[str, int]],
                type_=t.Dict[str, int],
                container_type="dict",
                args=[str, int],
                is_optional=True,
            ),
        ),
        (
            "optional dict str optional int",
            t.Optional[t.Dict[str, t.Optional[int]]],
            container(
                raw=t.Optional[t.Dict[str, t.Optional[int]]],
                type_=t.Dict[str, t.Optional[int]],
                container_type="dict",
                raw_args=[
                    atom(raw=str, underlying=str),
                    atom(
                        raw=t.Optional[int],
                        type_=int,
                        underlying=int,
                        is_optional=True,
                    ),
                ],
                is_optional=True,
            ),
        ),
        # schema
        (
            "user_defined_type",
            _Person,
            atom(raw=_Person, underlying=_Person, user_defined_type=_Person),
        ),
        (
            "optional user_defined_type",
            t.Optional[_Person],
            atom(
                raw=t.Optional[_Person],
                type_=_Person,
                underlying=_Person,
                user_defined_type=_Person,
                is_optional=True,
            ),
        ),
        (
            "list user_defined_type",
            t.List[_Person],
            container(
                raw=t.List[_Person],
                container_type="list",
                raw_args=[
                    atom(raw=_Person, underlying=_Person, user_defined_type=_Person)
                ],
            ),
        ),
        # composite
        (
            "union int str",
            t.Union[int, str],
            container(
                raw=t.Union[int, str],
                container_type="union",
                is_combined=True,
                raw_args=[atom(raw=int, underlying=int), atom(raw=str, underlying=str)],
            ),
        ),
        pytest.param(
            "union int str (pep604)",
            int | str,
            container(
                raw=t.Union[int, str],
                container_type="union",
                is_combined=True,
                raw_args=[atom(raw=int, underlying=int), atom(raw=str, underlying=str)],
            ),
            marks=pytest.mark.skipif(
                sys.version_info < (3, 10), reason="pep604 not supported"
            ),
        ),
        (
            "optional union optional user_defined_type optional str",
            # simplify -> t.Union[NoneType, _Person, str]
            t.Optional[t.Union[t.Optional[_Person], t.Optional[str]]],
            container(
                raw=t.Optional[t.Union[t.Optional[_Person], t.Optional[str]]],
                type_=t.Union[_Person, str],
                container_type="union",
                is_combined=True,
                is_optional=True,
                raw_args=[
                    atom(raw=_Person, underlying=_Person, user_defined_type=_Person),
                    atom(raw=str, underlying=str),
                ],
            ),
        ),
        # special
        (
            "newType",
            _MyString,
            atom(raw=_MyString, underlying=str, supertypes=[_MyString]),
        ),
        (
            "newType",
            _MyString2,
            atom(raw=_MyString2, underlying=str, supertypes=[_MyString2, _MyString]),
        ),
        (
            "optional newType",
            t.Optional[_MyString],
            atom(
                raw=t.Optional[_MyString],
                type_=_MyString,
                underlying=str,
                is_optional=True,
                supertypes=[_MyString],
            ),
        ),
        (
            "optional newType2",
            _Optional_MyString,
            atom(
                raw=_Optional_MyString,
                type_=_Optional_MyString,
                underlying=str,
                is_optional=True,
                supertypes=[_Optional_MyString],
            ),
        ),
        (
            "newType user defined",
            _MyPerson,
            atom(
                raw=_MyPerson,
                underlying=_Person,
                user_defined_type=_Person,
                supertypes=[_MyPerson],
            ),
        ),
        (
            "newType user defined with composite type",
            t.List[_MyPerson],
            container(
                raw=t.List[_MyPerson],
                container_type="list",
                raw_args=[
                    atom(
                        raw=_MyPerson,
                        underlying=_Person,
                        user_defined_type=_Person,
                        supertypes=[_MyPerson],
                    ),
                ],
            ),
        ),
        (
            "newType user defined with composite type with newType",
            _MyPeople,
            container(
                raw=_MyPeople,
                container_type="list",
                raw_args=[
                    atom(
                        raw=_MyPerson,
                        underlying=_Person,
                        user_defined_type=_Person,
                        supertypes=[_MyPerson],
                    ),
                ],
                supertypes=[_MyPeople],
            ),
        ),
        (
            "stringLiteral",
            tx.Literal["A", "B"],
            atom(raw=tx.Literal["A", "B"], underlying=str),
        ),
        (
            "optional stringLiteral",
            t.Optional[tx.Literal["A", "B"]],
            atom(
                raw=t.Optional[tx.Literal["A", "B"]],
                type_=tx.Literal["A", "B"],
                underlying=str,
                is_optional=True,
            ),
        ),
    ],
)
def test_type_info(msg: str, typ, want):
    from metashape.typeinfo import typeinfo as callFUT

    got = callFUT(typ)
    assert got == want
