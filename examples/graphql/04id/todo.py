import typing as t
from metashape.types import ID


class Todo:
    id: ID
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]
