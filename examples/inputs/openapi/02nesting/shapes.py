from __future__ import annotations
import typing


class Memo:
    title: str
    content: str


class Person:
    name: str
    age: typing.Optional[str]
    memo: Memo
    optional_memo: typing.Optional[Memo]  # original is optional-memo
