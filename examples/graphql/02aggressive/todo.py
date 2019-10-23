import typing as t


class Todo:
    id: str
    name: t.Optional[str]
    description: t.Optional[str]
    priority: t.Optional[int]
