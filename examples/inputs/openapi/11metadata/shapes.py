from __future__ import annotations
import typing


class ErrorModel:
    message: str
    # metadata: {'type': 'string', 'required': True}
    code: int
    # metadata: {'type': 'integer', 'minimum': 100, 'maximum': 600, 'required': True}
    status: typing.Optional[str]
    # metadata: {'type': 'string', 'readOnly': True, 'required': False}
    statusCode: typing.Optional[int]
    # metadata: {'type': 'integer', 'minimum': 100, 'maximum': 600, 'deprecated': True, 'required': False}


class Toplevel:
    errors: typing.Optional[typing.List[ErrorModel]]
    # metadata: {'required': False}
