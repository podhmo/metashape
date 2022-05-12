from metashape.declarative import mark
from metashape.runtime import get_walker
from metashape.outputs.openapi import codegen


@mark
class Person:
    name: str
    age: int

    @classmethod
    def __defaults__(cls, d):
        d["defaults"] = [{"id": 1, "name": "foo"}]


# main
codegen(get_walker([Person]), hooks=["__defaults__"])
