from metashape.declarative import mark
from metashape.runtime import get_walker
from metashape.outputs.openapi import codegen


@mark
class Person:
    name: str
    age: int


# main
codegen(get_walker([Person]))
