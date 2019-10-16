import typing as t
import typing_extensions as tx
import pytest
from metashape.analyze import typeinfo


class Person:
    name: str


@pytest.mark.parametrize(
    "input, want",
    [
        (int, "integer"),
        (float, "number"),
        (str, "string"),
        (bool, "boolean"),
        (Person, "object"),
        # (None, "null"),
        #
        (t.Optional[int], "integer"),
        (t.Optional[float], "number"),
        (t.Optional[str], "string"),
        (t.Optional[bool], "boolean"),
        (t.Optional[Person], "object"),
        #
        (dict, "object"),
        (t.Dict, "object"),
        #
        (list, "array"),
        (tuple, "array"),
        (t.List[int], "array"),
        #
        (t.Optional[t.List[int]], "array"),
        (t.List[t.Optional[int]], "array"),
        #
        (tx.Literal["N", "S", "E", "W"], "string"),
    ],
)
def test_schema_type(input, want):
    from metashape.flavors.openapi.detect import schema_type as callFUT

    info = typeinfo.detect(input)
    got = callFUT(info)
    assert got == want


@pytest.mark.parametrize(
    "input, want",
    [
        (int, ()),
        (str, ()),
        (tx.Literal["N", "S", "E", "W"], ("N", "S", "E", "W")),
        (t.Optional[tx.Literal["N", "S", "E", "W"]], ("N", "S", "E", "W")),
    ],
)
def test_enum(input, want):
    from metashape.flavors.openapi.detect import enum as callFUT

    info = typeinfo.detect(input)
    got = callFUT(info)
    assert got == want
