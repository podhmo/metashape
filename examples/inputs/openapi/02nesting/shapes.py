from __future__ import annotations
import typing
from metashape.declarative import (
    field,
    ORIGINAL_NAME,
)


class Memo:
    title: str
    content: str


class Person:
    name: str
    age: typing.Optional[int]
    memo: Memo
    optional_memo: typing.Optional[Memo] = field(metadata={ORIGINAL_NAME: 'optional-memo'})
