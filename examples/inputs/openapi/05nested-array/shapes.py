import typing


class Person:
    name: str
    age: typing.Optional[str]
    children: typing.Optional[typing.List[Person]]
    children2: typing.List[Person]
    children3: typing.List[Person]
    children4: typing.List[PersonChildren4Item]
    Nchildren: typing.List[typing.List[Person]]
    Nchildren2: typing.Optional[typing.List[typing.List[Person]]]
    Nchildren3: typing.List[typing.List[Person]]
    Nchildren4: typing.List[typing.List[Person]]
    Nchildren5: typing.List[typing.List[PersonNchildren5ItemItem]]


class PersonNchildren5ItemItem:
    name: str
    age: typing.Optional[str]
    Nchildren: typing.Optional[typing.List[Person]]


class PersonChildren4Item:
    name: str
    age: typing.Optional[str]
    children: typing.Optional[typing.List[Person]]
