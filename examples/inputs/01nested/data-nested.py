from typing import List, Optional


class Data:
    class Parent:
        age: int
        name: str
        nickname: Optional[str]

    age: int
    name: str
    parents: List['Parent']


