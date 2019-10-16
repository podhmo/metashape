import typing as t
import typing_extensions as tx
import pytest


_MyString = t.NewType("S", str)


class _Person:
    name: str


def atom(*, raw, underlying=None, normalized=None, is_optional=False, custom=None):
    return {
        "raw": raw,
        "underlying": underlying or raw,
        "normalized": normalized or raw or underlying,
        "is_optional": is_optional,
        "custom": custom,
    }


def container(
    *,
    container,
    raw,
    normalized=None,
    is_optional=False,
    is_composite=False,
    raw_args=None,
    args=None
):
    raw_args = raw_args or [atom(raw=x, underlying=x) for x in args]
    return {
        "raw": raw,
        "normalized": normalized or raw,
        "args": tuple(raw_args),
        "container": container,
        "is_optional": is_optional,
        "is_composite": is_composite,
    }


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
    from metashape.analyze.typeinfo import omit_optional as callFUT

    got = callFUT(typ)
    assert got == (want, omitted)


@pytest.mark.parametrize(
    "typ, want",
    [
        (int, atom(raw=int, underlying=int)),
        (str, atom(raw=str, underlying=str)),
        (
            t.Optional[str],
            atom(raw=t.Optional[str], normalized=str, underlying=str, is_optional=True),
        ),
        # container
        (t.List[str], container(raw=t.List[str], container="list", args=[str])),
        (
            t.Optional[t.List[str]],
            container(
                raw=t.Optional[t.List[str]],
                normalized=t.List[str],
                container="list",
                args=[str],
                is_optional=True,
            ),
        ),
        (
            t.List[t.Optional[str]],
            container(
                raw=t.List[t.Optional[str]],
                container="list",
                raw_args=[
                    atom(
                        raw=t.Optional[str],
                        normalized=str,
                        underlying=str,
                        is_optional=True,
                    )
                ],
            ),
        ),
        (list, container(raw=list, normalized=t.Sequence, container="list", args=[t.Any])),
        (
            t.Tuple[str],
            container(
                raw=t.Tuple[str], container="tuple", args=[str]
            ),
        ),
        (
            t.Tuple[str, int],
            container(raw=t.Tuple[str, int], container="tuple", args=[str, int]),
        ),
        (
            t.Dict[str, int],
            container(raw=t.Dict[str, int], container="dict", args=[str, int]),
        ),
        (
            t.Optional[t.Dict[str, int]],
            container(
                raw=t.Optional[t.Dict[str, int]],
                normalized=t.Dict[str, int],
                container="dict",
                args=[str, int],
                is_optional=True,
            ),
        ),
        (
            t.Optional[t.Dict[str, t.Optional[int]]],
            container(
                raw=t.Optional[t.Dict[str, t.Optional[int]]],
                normalized=t.Dict[str, t.Optional[int]],
                container="dict",
                raw_args=[
                    atom(raw=str, underlying=str),
                    atom(
                        raw=t.Optional[int],
                        normalized=int,
                        underlying=int,
                        is_optional=True,
                    ),
                ],
                is_optional=True,
            ),
        ),
        # schema
        (_Person, atom(raw=_Person, underlying=_Person, custom=_Person)),
        (
            t.Optional[_Person],
            atom(
                raw=t.Optional[_Person],
                normalized=_Person,
                underlying=_Person,
                custom=_Person,
                is_optional=True,
            ),
        ),
        (
            t.List[_Person],
            container(
                raw=t.List[_Person],
                container="list",
                raw_args=[atom(raw=_Person, underlying=_Person, custom=_Person)],
            ),
        ),
        # composite
        (
            t.Union[int, str],
            container(
                raw=t.Union[int, str],
                container="union",
                is_composite=True,
                raw_args=[atom(raw=int, underlying=int), atom(raw=str, underlying=str)],
            ),
        ),
        (
            # simplify -> t.Union[NoneType, _Person, str]
            t.Optional[t.Union[t.Optional[_Person], t.Optional[str]]],
            container(
                raw=t.Optional[t.Union[t.Optional[_Person], t.Optional[str]]],
                normalized=t.Union[_Person, str],
                container="union",
                is_composite=True,
                is_optional=True,
                raw_args=[
                    atom(raw=_Person, underlying=_Person, custom=_Person),
                    atom(raw=str, underlying=str),
                ],
            ),
        ),
        # special
        (_MyString, atom(raw=_MyString, underlying=str)),
        (
            t.Optional[_MyString],
            atom(
                raw=t.Optional[_MyString],
                normalized=_MyString,
                underlying=str,
                is_optional=True,
            ),
        ),
        (tx.Literal["A", "B"], atom(raw=tx.Literal["A", "B"], underlying=str)),
        (
            t.Optional[tx.Literal["A", "B"]],
            atom(
                raw=t.Optional[tx.Literal["A", "B"]],
                normalized=tx.Literal["A", "B"],
                underlying=str,
                is_optional=True,
            ),
        ),
    ],
)
def test_resolve_type_info(typ, want):
    from metashape.analyze.typeinfo import detect as callFUT

    got = callFUT(typ)
    assert got == want