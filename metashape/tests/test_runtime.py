# type: ignore
import pytest
import dataclasses


CODE = """\
from __future__ import annotations
import typing as t

class A:
    b: B
    cs: t.List[C]
    i: I

class B:
    d: D
    es: t.Optional[E]
    i: I

class C:
    f: F
    gs: t.Dict[G, H]
    i: I

class D:
    name: str

class E:
    name: str

class F:
    name: str

class G:
    name: str

class H:
    name: str

class I:
    name: str
"""


@dataclasses.dataclass(frozen=True)
class C:
    aggressive: bool = False
    recursive: bool = False


@pytest.mark.parametrize(
    "msg, c, input, want",
    [
        ("one", C(), lambda m: m.A, ["A"]),
        ("one, aggressive=True", C(aggressive=True), lambda m: m.A, ["A"]),
        ("one, recursive=True", C(recursive=True), lambda m: m.A, ["A"]),
        (
            "one, aggressive=True, recursive=True",
            C(aggressive=True, recursive=True),
            lambda m: m.A,
            ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
        ),
        ("list", C(), lambda m: [m.A, m.B], ["A", "B"]),
        ("list, aggressive=True", C(aggressive=True), lambda m: [m.A, m.B], ["A", "B"]),
        (
            "list, aggressive=True, recursive=True",
            C(aggressive=True, recursive=True),
            lambda m: [m.A, m.B],
            ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
        ),
        (
            "dict, aggressive=True, recursive=True",
            C(aggressive=True, recursive=True),
            lambda m: {"A": m.A, "B": m.B},
            ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
        ),
    ],
)
def test_walker(msg, c, input, want):
    from metashape.runtime import get_walker as callFUT
    from metashape.analyze.config import Config

    def _create_module(code: str):
        from magicalimport import import_from_physical_path
        import tempfile

        # create fake module
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as wf:
            print(code, file=wf)
            wf.flush()
            return import_from_physical_path(wf.name)

    m = _create_module(CODE)
    nodes = callFUT(
        input(m),
        aggressive=c.aggressive,
        config=Config(Config.Option(recursive=c.recursive)),
    ).walk()
    got = [cls.__name__ for cls in nodes]

    assert len(got) == len(want)
    assert set(got) == set(want)
