import typing as t
from metashape.declarative import mark
from metashape.runtime import get_walker
from metashape.outputs.graphql import codegen


@mark
class Todo:
    id: str
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]


# main
codegen(get_walker([Todo]))
