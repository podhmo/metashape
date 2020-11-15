import typing


class Memo:
    title: str
    content: str


class Person:
    name: str
    age: typing.Optional[str]
    memo: Memo
    optional_memo: Memo  # original is optional-memo
