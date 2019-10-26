from metashape.declarative import mark
from metashape.shortcuts import compile_with
from metashape.outputs.openapi import emit


@mark
class Person:
    name: str
    age: int


# main
compile_with([Person], emit=emit)
