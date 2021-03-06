from __future__ import annotations
from metashape.declarative import (
    field,
    ORIGINAL_NAME,
)
import typing


# metadata: {'description': 'this is error model', 'type': 'object'}
class ErrorModel:
    """
    this is error model
    """

    message: str
    code: int = field(metadata={'openapi': {'type': 'integer', 'minimum': 100, 'maximum': 600, 'required': True}})
    status: typing.Optional[str] = field(metadata={'openapi': {'type': 'string', 'readOnly': True, 'required': False}})
    statusCode: typing.Optional[int] = field(metadata={'openapi': {'type': 'integer', 'minimum': 100, 'maximum': 600, 'deprecated': True, 'required': False}})


# metadata: {'type': 'object'}
class Toplevel:
    errors: typing.Optional[typing.List[ErrorModel]] = field(metadata={'openapi': {'required': False, 'description': 'list of error model', 'type': 'array', 'minItems': 1, 'maxItems': 3}})
    errors_inline: typing.Optional[typing.List[ErrorModel]] = field(metadata={ORIGINAL_NAME: 'errors-inline', 'openapi': {'type': 'array', 'minItems': 1, 'maxItems': 3, 'required': False}})
    date: typing.Optional[str] = field(metadata={'openapi': {'required': False, 'type': 'string', 'pattern': '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]?\\d{2}:\\d{2})'}})
    inline_date: typing.Optional[str] = field(metadata={ORIGINAL_NAME: 'inline-date', 'openapi': {'type': 'string', 'pattern': '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]?\\d{2}:\\d{2})', 'required': False}})
