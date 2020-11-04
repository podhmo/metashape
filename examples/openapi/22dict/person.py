from __future__ import annotations
import typing as t


class Person:
    name: str
    age: int
    data: t.Dict[str, str]
    nested_data: t.Dict[str, t.Dict[str, str]]
