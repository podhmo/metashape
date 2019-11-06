from __future__ import annotations
import typing as t

# spec
# - the information about inheritance is squached
# - private instance variables are ignored (the name starts with "_")
# - private classes are ignored (the name starts with "_")
# - TODO: support property?
# - TODO: metadata for inheritance?


class BasePerson:
    name: str
    age: int


class _WithMemo:
    memo: t.Optional[str]


class Person(BasePerson, _WithMemo):
    age: t.Optional[int]
    nickname: t.Optional[str]
    _private: int
