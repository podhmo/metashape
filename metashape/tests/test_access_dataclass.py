# type: ignore
from __future__ import annotations
import typing as t
import dataclasses
import pytest


class Description:
    def __init__(self, description: str) -> None:
        self.description = description

    def __repr__(self) -> repr:
        return f"Description({self.description})"


@dataclasses.dataclass
class Simple:
    name: str


@dataclasses.dataclass
class Many:
    memo: t.List[str] = dataclasses.field(default_factory=list)


# # not supported
# @dataclasses.dataclass
# class WithAnnotated:
#     name: tx.Annotated[str, Description("name of object")]  # noqa: F722


@dataclasses.dataclass
class WithAnnotated:
    name: str = dataclasses.field(metadata={"description": "name of object"})


@dataclasses.dataclass
class CodehiliteExtension:
    codehilite: Data
    name: str

    @dataclasses.dataclass
    class Data:
        guess_lang: bool


@dataclasses.dataclass
class TocExtension:
    toc: TocExtension.Data
    name: str

    @dataclasses.dataclass
    class Data:
        permalink: bool


@pytest.mark.parametrize(
    "msg, target_class, want",
    [
        ("simple", Simple, {"name": {"type": str, "metadata": {}}}),
        ("many", Many, {"memo": {"type": t.List[str], "metadata": {}}}),
        (
            "with-annotated",
            WithAnnotated,
            {"name": {"type": str, "metadata": {"description": "name of object"}}},
        ),
        (
            "internal-def",
            CodehiliteExtension,
            {
                "codehilite": {"type": CodehiliteExtension.Data, "metadata": {}},
                "name": {"type": str, "metadata": {}},
            },
        ),
        (
            "internal-def2",
            TocExtension,
            {
                "toc": {"type": TocExtension.Data, "metadata": {}},
                "name": {"type": str, "metadata": {}},
            },
        ),
    ],
)
def test_iterate_props(msg, target_class, want):
    from metashape._dataclass import iterate_props as _callFUT

    got = {
        name: {
            "type": typ,
            **({"metadata": dict(metadata)} if metadata is not None else {}),
        }
        for name, typ, metadata in _callFUT(target_class)
    }

    import json

    assert json.dumps(got, default=str) == json.dumps(want, default=str)
