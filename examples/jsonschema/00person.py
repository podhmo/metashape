from metashape.declarative import mark
from metashape.shortcuts import compile_with


@mark
class Person:
    name: str
    age: int


# main
compile_with([Person])
