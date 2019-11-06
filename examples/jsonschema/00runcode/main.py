from metashape.declarative import mark
from metashape.runtime import emit_with
from metashape.outputs.jsonschema import emit


@mark
class Person:
    name: str
    age: int


# main
emit_with([Person], emit=emit)
