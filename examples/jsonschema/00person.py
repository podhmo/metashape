from metashape.declarative import mark
from metashape import compile as c


@mark
class Person:
    name: str
    age: int


# main
print(
    c.compile(
        c.Accessor(resolver=c.FakeResolver(), repository=c.FakeRepository([Person]))
    )
)
