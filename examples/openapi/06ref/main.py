from metashape.declarative import mark
from metashape.shortcuts import compile_with
from metashape.drivers.openapi import emit


@mark
class Person:
    name: str
    age: int
    extra: "Extra"


@mark
class Extra:
    memo: str


# main
compile_with([Person], emit=emit)
