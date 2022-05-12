from __future__ import annotations
import typing as t


class Person:
    name: str
    age: int

    memo: str | int
    memoList: t.List[str | int]

    parents: t.List[Person]
    pets: t.List[Dog | Cat]


class Dog:
    bark: bool
    breed: str
    age: int


class Cat:
    hunts: bool
    age: int
