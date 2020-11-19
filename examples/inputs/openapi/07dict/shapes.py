from __future__ import annotations
import typing


class Person:
    name: str
    age: int
    parents: typing.Optional[typing.Dict[str, Person]]
    parents2: typing.Optional[typing.Dict[str, Person]]
