from __future__ import annotations
import typing as t


# from https://docs.ponyorm.org/relationships.html
# self references
class Person:
    name: str
    spouse: t.Optional[Person]  # reverse: spouse,  synmetric one-to-one
    friends: t.Set[Person]  # reverse: friends, synmetric many-to-many
    manager: t.Optional[Person]  # reverse: employees, one side of non-synmetric
    employees: t.Set[Person]  # reverse: manager, another side of non-synmetric
