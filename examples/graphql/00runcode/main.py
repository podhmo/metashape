import typing as t
from metashape.declarative import mark
from metashape.shortcuts import compile_with
from metashape.drivers.graphql import emit


@mark
class Todo:
    id: str
    name: t.Optional[str]
    description: t.Optional[str]
    priority: t.Optional[int]


# main
compile_with([Todo], emit=emit)
