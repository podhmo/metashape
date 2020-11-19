from __future__ import annotations
import typing


class Palette:
    main: typing.Literal['black', 'white', 'red', 'green', 'blue']
    sort: typing.Optional[typing.Literal['asc', 'desc']]
    sub1: typing.Optional[typing.Literal['black', 'white', 'red', 'green', 'blue']]
    sub2: typing.Optional[typing.Literal['black', 'white', 'red', 'green', 'blue']]
