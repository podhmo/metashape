from __future__ import annotations
import typing


class Person:
    name: str
    age: typing.Optional[str]
    children: typing.Optional[typing.List[Person]]
    children2: typing.Optional[typing.List[Person]]
    children3: typing.Optional[typing.List[Person]]
    children4: typing.Optional[typing.List[_PersonChildren4Item]]
    Nchildren: typing.Optional[typing.List[typing.List[Person]]]
    Nchildren2: typing.Optional[typing.List[typing.List[Person]]]
    Nchildren3: typing.Optional[typing.List[typing.List[Person]]]
    Nchildren4: typing.Optional[typing.List[typing.List[Person]]]
    Nchildren5: typing.Optional[typing.List[typing.List[_PersonNchildren5ItemItem]]]


class _PersonNchildren5ItemItem:
    name: str
    age: typing.Optional[str]
    Nchildren: typing.Optional[typing.List[Person]]


class _PersonChildren4Item:
    name: str
    age: typing.Optional[str]
    children: typing.Optional[typing.List[Person]]
