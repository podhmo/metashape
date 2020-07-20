from __future__ import annotations
import typing as t


class User:
    name: str


# todo: use metashape.name.NewNamedType ?
UserList = t.List[User]


class Toplevel:
    named: UserList
    unnamed: t.List[User]
