from __future__ import annotations
import typing
from metadata.declarative import field


class Palette:
    main: typing.Literal['black', 'white', 'red', 'green', 'blue'] = field()
    sort: typing.Optional[typing.Literal['asc', 'desc']] = field(metadata={'openapi': {'description': 'inline enums'}})
    sub1: typing.Optional[typing.Literal['black', 'white', 'red', 'green', 'blue']] = field(metadata={'openapi': {'description': 'Nullable enums', 'nullable': True}})
    sub2: typing.Optional[typing.Literal['black', 'white', 'red', 'green', 'blue']] = field(metadata={'openapi': {'description': 'Nullable enums', 'nullable': True}})
