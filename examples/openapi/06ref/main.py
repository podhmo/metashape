from metashape.declarative import mark
from metashape.runtime import emit_with
from metashape.outputs.openapi import emit


@mark
class Person:
    name: str
    age: int
    extra: "Extra"


@mark
class Extra:
    memo: str


# main
emit_with([Person], emit=emit)
