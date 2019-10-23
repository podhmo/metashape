from __future__ import annotations
import typing as t


class Board:
    lanes: t.Optional[t.List[Lane]]
    mlanes: t.Optional[t.List[t.Optional[Lane]]]


class Lane:
    name: str
    todos: t.List[Todo]


class Todo:
    id: str
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]
