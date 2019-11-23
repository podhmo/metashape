from metashape.outputs.openapi import codegen
from metashape.runtime import get_walker, Config


class Person:
    name: str
    age: int


config = Config(Config.Option(strict=False))
codegen(get_walker(aggressive=True, config=config))
