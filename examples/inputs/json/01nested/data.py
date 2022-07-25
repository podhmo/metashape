from typing import List, Optional


class Data:
    age: int
    name: str
    parents: List['Parent']


class Parent:
    age: int
    name: str
    nickname: Optional[str]


