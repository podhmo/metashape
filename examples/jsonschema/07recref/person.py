class Person:
    name: str
    age: int
    father: "Person"  # todo: optional
    mother: "Person"
    extra: "Extra"


class Extra:
    memo: str
