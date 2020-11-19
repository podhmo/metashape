from __future__ import annotations
import typing


class Person:
    name: str
    age: typing.Optional[str]
    father: typing.Optional[Person]
    mother: typing.Optional[Person]
