import typing as t


class Todo:
    id: str
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]
