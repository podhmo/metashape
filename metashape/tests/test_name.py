# type: ignore
from metashape.name import guess_name as callFUT


def test_primitives():
    assert callFUT(int) == "int"
    assert callFUT(float) == "float"
    assert callFUT(str) == "str"
    assert callFUT(dict) == "dict"
    assert callFUT(list) == "list"


class OuterA:
    pass


def test_classes():
    from collections import ChainMap
    from collections import namedtuple

    class InnerA:
        pass

    Color = namedtuple("Color", "r, g, b")

    assert callFUT(OuterA) == "OuterA"
    assert callFUT(InnerA) == "InnerA"
    assert callFUT(ChainMap) == "ChainMap"
    assert callFUT(Color) == "Color"


def test_generics():
    import typing as t

    IntList = t.List[int]
    StrTuple1 = t.Tuple[str]
    StrTupleN = t.Tuple[str, ...]
    Commands = t.Dict[str, t.Callable[..., t.Any]]

    class Person:
        pass

    PersonDict = t.Dict[str, Person]

    assert callFUT(IntList) == "IntList"
    assert callFUT(StrTuple1) == "StrTuple"
    assert callFUT(StrTupleN) == "StrNTuple"
    assert callFUT(PersonDict) == "StrPersonDict"
    assert callFUT(Commands) == "StrNReturnAnyCallableDict"


def test_Literal():
    from typing_extensions import Literal

    Op = Literal["add", "sub", "mul"]
    Op.__name__ = "Op"
    assert callFUT(Op) == "Op"
    assert callFUT(Literal["add", "sub", "mul"]) == "Op"
    assert callFUT(Literal["mul", "sub", "add"]) == "MulorSuborAdd"


def test_Union():
    from typing import Union

    class X:
        pass

    class Y:
        pass

    XorY = Union[X, Y]
    XorY.__name__ = "XorY"
    assert callFUT(XorY) == "XorY"
    assert callFUT(Union[X, Y]) == "XorY"
    assert callFUT(Union[Y, X]) == "XorY"


def test_NewType():
    from typing import NewType

    uint64 = NewType("uint64", int)
    uint32 = NewType("uint32", int)

    assert callFUT(uint64) == "uint64"
    assert callFUT(uint32) == "uint32"
