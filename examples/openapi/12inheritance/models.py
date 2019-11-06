from __future__ import annotations
import typing as t


class BasePerson:
    name: str
    age: int


class _WithMemo:
    memo: t.Optional[str]


class Person(BasePerson, _WithMemo):
    age: t.Optional[int]
    nickname: t.Optional[str]
    _private: int
