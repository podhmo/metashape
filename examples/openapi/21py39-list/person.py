from __future__ import annotations
import sys
import typing as t

py39List = list
if sys.version_info < (3, 9):
    py39List = t.List


class Person:
    name: str
    age: int
    parents: py39List[Person]
    skills: t.Optional[py39List[str]]
