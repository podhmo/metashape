from metashape.outputs.openapi import emit
from metashape.runtime import get_walker, Config


class Person:
    name: str
    age: int


config = Config(Config.Option(strict=False))
emit(get_walker(aggressive=True, config=config))
