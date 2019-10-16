import typing as t


class Person:
    name: str
    age: int
    father: "Person"  # invalid: infinite recursion is occured
    mother: t.Optional["Person"]
    extra: "Extra"


class Extra:
    memo: str
