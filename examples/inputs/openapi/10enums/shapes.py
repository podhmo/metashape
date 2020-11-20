from __future__ import annotations
import typing
from metadata.declarative import field


class Palette:
    main: typing.Literal['black', 'white', 'red', 'green', 'blue'] = field(metadata={'openapi': {'enum': ['black', 'white', 'red', 'green', 'blue']}})
    sort: typing.Optional[typing.Literal['asc', 'desc']] = field(metadata={'openapi': {'description': 'inline enums', 'enum': ['asc', 'desc']}})
    sub1: typing.Optional[typing.Literal['black', 'white', 'red', 'green', 'blue']] = field(metadata={'openapi': {'description': 'Nullable enums', 'enum': ['black', 'white', 'red', 'green', 'blue', None], 'nullable': True}})
    sub2: typing.Optional[typing.Literal['black', 'white', 'red', 'green', 'blue']] = field(metadata={'openapi': {'description': 'Nullable enums', 'enum': ['black', 'white', 'red', 'green', 'blue', None], 'nullable': True}})
