import typing as t
from metashape.declarative import mark


@mark
class Todo:
    id: str
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]
