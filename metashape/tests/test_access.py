# type: ignore
from __future__ import annotations
import typing as t
import typing_extensions as tx
import pytest
from metashape._access import SeeArgsForMetadata


# TODO: this is flake8's bug, string value is treated as type
# metashape/tests/test_access.py:59:39: F722 syntax error in forward annotation 'nickname of object'
# metashape/tests/test_access.py:64:52: F821 undefined name 'parents'


class Description:
    def __init__(self, description: str) -> None:
        self.description = description

    def __repr__(self) -> repr:
        return f"Description({self.description})"


class Description2:
    def __init__(self, message: repr) -> None:
        self.message = message

    def as_metadata(self) -> t.Dict[repr, t.Any]:
        return {"description": self.message}

    def __repr__(self) -> repr:
        return f"Description({self.message})"


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


class Nested:
    name: str
    person: _Person

    class _Person:
        name: str
        age: int


class WithAnnotated:
    name: tx.Annotated[str, Description("name of object")]  # noqa: F722


class WithAnnotatedAsMetadata:
    name: tx.Annotated[str, Description2("name of object")]  # noqa: F722


class WithAnnotatedOptional:
    nickname: tx.Annotated[
        t.Optional[str], Description("nickname of object")  # noqa: F722
    ]


class WithAnnotatedOptional2:
    nickname: t.Optional[
        tx.Annotated[str, Description("nickname of object")]  # noqa: F722,F821
    ]


class WithAnnotatedList:
    parents: tx.Annotated[t.List[str], Description("parents")]  # noqa: F821
    parents2: t.List[
        tx.Annotated[str, Description("parents")]  # noqa: F821
    ]  # not extract
    parents3: tx.Annotated[
        t.List[tx.Annotated[str, Description("parents")]],  # noqa: F821
        SeeArgsForMetadata(),
    ]


class WithAnnotatedComplexNested:
    complex_nested: t.Dict[
        str, t.Dict[str, tx.Annotated[str, Description("complex_nested")]]  # noqa: F821
    ]
    complex_nested2: tx.Annotated[
        t.Dict[
            str,
            t.Dict[str, tx.Annotated[str, Description("complex_nested")]],  # noqa: F821
        ],
        SeeArgsForMetadata(),
    ]


@pytest.mark.parametrize(
    "msg, target_class, want",
    [
        (
            "base",
            Person,
            {
                "name": {"type": str, "metadata": {}},
                "age": {"type": int, "metadata": {}},
            },
        ),
        (
            "inherited",
            ActualPerson,
            {
                "name": {"type": str, "metadata": {}},
                "age": {"type": t.Optional[int], "metadata": {}},
                "nickname": {"type": t.Optional[str], "metadata": {}},
            },
        ),
        ("ignore-private", WithPrivate, {"name": {"type": str, "metadata": {}}}),
        (
            "annotated",
            WithAnnotated,
            {"name": {"type": str, "metadata": {"description": "name of object"}}},
        ),
        # nested
        (
            "nested",
            Nested,
            {
                "name": {"type": str, "metadata": {}},
                "person": {"type": Nested._Person, "metadata": {}},
            },
        ),
        # annotation
        (
            "annotated-as-metadata",
            WithAnnotatedAsMetadata,
            {"name": {"type": str, "metadata": {"description": "name of object"}}},
        ),
        (
            "annotated-with-optional",
            WithAnnotatedOptional,
            {
                "nickname": {
                    "type": t.Optional[str],
                    "metadata": {"description": "nickname of object"},
                },
            },
        ),
        (
            "annotated-with-optional2",
            WithAnnotatedOptional2,
            {
                "nickname": {
                    "type": t.Optional[str],
                    "metadata": {"description": "nickname of object"},
                },
            },
        ),
        (
            "annotated-with-see_args",
            WithAnnotatedList,
            {
                "parents": {
                    "type": t.List[str],
                    "metadata": {"description": "parents"},
                },
                "parents2": {
                    "type": t.List[tx.Annotated[str, Description("parents")]],
                    "metadata": {},
                },
                "parents3": {
                    "type": t.List[str],
                    "metadata": {"description": "parents"},
                },
            },
        ),
        (
            "annotated-with-see_args2",
            WithAnnotatedComplexNested,
            {
                "complex_nested": {
                    "type": t.Dict[
                        str,
                        t.Dict[str, tx.Annotated[str, Description("complex_nested")]],
                    ],
                    "metadata": {},
                },
                "complex_nested2": {
                    "type": t.Dict[str, t.Dict[str, str]],
                    "metadata": {"description": "complex_nested"},
                },
            },
        ),
        # TODO: property?
    ],
)
def test_iterate_props(msg, target_class, want):
    from metashape._access import iterate_props as _callFUT

    got = {
        name: {
            "type": typ,
            **({"metadata": dict(metadata)} if metadata is not None else {}),
        }
        for name, typ, metadata in _callFUT(target_class)
    }

    import json

    assert json.dumps(got, default=str) == json.dumps(want, default=str)
