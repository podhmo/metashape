import typing as t
from metashape.declarative import mark
from metashape.runtime import emit_with
from metashape.outputs.graphql import emit


@mark
class Todo:
    id: str
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]


# main
emit_with([Todo], emit=emit)
