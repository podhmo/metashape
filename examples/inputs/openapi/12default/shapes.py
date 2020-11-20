from __future__ import annotations
import typing
from metadata.declarative import field


class Value:
    pi: typing.Optional[float] = field(default='3.14')


class Person:
    name: str = field(default='foo')
    age: typing.Optional[int] = field(default=0)
    gender: typing.Literal['male', 'feamale', 'unknown'] = field(default='unknown')
