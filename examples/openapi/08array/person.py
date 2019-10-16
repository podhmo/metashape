import typing as t


class Person:
    name: str
    age: int
    parents: t.List["Person"]
    skills: t.Optional[t.List[str]]
