from __future__ import annotations
import typing


class S:
    x: typing.Optional[typing.Dict[str, S]]
    y: typing.Optional[typing.Dict[str, S]]
    y2: typing.Optional[typing.Dict[str, S]]
    z: typing.Optional[typing.Dict[str, S]]
    z2: typing.Optional[typing.Dict[str, typing.Dict[str, S]]]
