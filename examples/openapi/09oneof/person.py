from __future__ import annotations
import typing as t


class Person:
    name: str
    age: int

    memo: t.Union[str, int]
    memoList: t.List[t.Union[str, int]]

    parents: t.List["Person"]
    pets: t.List[t.Union[Dog, Cat]]


class Dog:
    bark: bool
    breed: str
    age: int


class Cat:
    hunts: bool
    age: int
