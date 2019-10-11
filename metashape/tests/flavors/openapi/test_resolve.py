import typing as t
import pytest


class Person:
    name: str


@pytest.mark.parametrize(
    "input, want",
    [
        (int, {"type": "integer", "optional": False}),
        (float, {"type": "number", "optional": False}),
        (str, {"type": "string", "optional": False}),
        (bool, {"type": "boolean", "optional": False}),
        (Person, {"type": "object", "optional": False}),
        # (None, {"type": "null", "optional": False}),
        #
        (t.Optional[int], {"type": "integer", "optional": True}),
        (t.Optional[float], {"type": "number", "optional": True}),
        (t.Optional[str], {"type": "string", "optional": True}),
        (t.Optional[bool], {"type": "boolean", "optional": True}),
        (t.Optional[Person], {"type": "object", "optional": True}),
        #
        (dict, {"type": "object", "optional": False}),
        (t.Dict, {"type": "object", "optional": False}),
        #
        (list, {"type": "array", "optional": False}),
        (tuple, {"type": "array", "optional": False}),
        (t.List[int], {"type": "array", "optional": False}),
        #
        (t.Optional[t.List[int]], {"type": "array", "optional": True}),
        (t.List[t.Optional[int]], {"type": "array", "optional": False}),
    ],
)
def test_resolve_type_info(input, want):
    from metashape.flavors.openapi.resolve import resolve_type_info as callFUT

    got = callFUT(input)
    assert got == want
