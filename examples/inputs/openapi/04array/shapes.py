from __future__ import annotations
import typing


class Person:
    name: str
    age: typing.Optional[str]
    children: typing.Optional[typing.List[Person]]
    children2: typing.Optional[typing.List[Person]]
