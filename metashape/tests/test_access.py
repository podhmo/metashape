# type: ignore
import typing as t
import pytest


@pytest.mark.parametrize(
    "msg, clsname, want",
    [
        ("base", "Person", {"name": str, "age": int}),
        (
            "inherited",
            "ActualPerson",
            {"name": str, "age": t.Optional[int], "nickname": t.Optional[str]},
        ),
        ("ignore-private", "WithPrivate", {"name": str}),
        # TODO: property?
    ],
)
def test_iterate_props(msg, clsname, want):
    import typing as t
    from metashape._access import iterate_props as _callFUT

    class Person:
        name: str
        age: int

    class ActualPerson(Person):
        age: t.Optional[int]
        nickname: t.Optional[str]

    class WithPrivate:
        name: str
        _private_val: str
        __dunder_val__: str

    target_class = locals()[clsname]  # xxx:
    got = {name: typ for name, typ, _ in _callFUT(target_class)}
    assert got == want
