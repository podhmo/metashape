from typing_extensions import Annotated


class Description:
    def __init__(self, description: str) -> None:
        self.description = description


class Description2:
    __slots__ = ("description",)

    def __init__(self, description: str) -> None:
        self.description = description


class Person:
    name: Annotated[str, Description("name of person")]
    age: Annotated[int, Description2("age of person")]
