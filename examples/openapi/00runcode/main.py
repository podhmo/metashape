from metashape.declarative import mark
from metashape.runtime import get_walker
from metashape.outputs.openapi import emit


@mark
class Person:
    name: str
    age: int


# main
emit(get_walker([Person]))
