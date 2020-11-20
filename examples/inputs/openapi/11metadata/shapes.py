from __future__ import annotations
from metadata.declarative import (
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
    # metadata: {'type': 'string', 'required': True}
    code: int = field(metadata={'openapi': {'minimum': 100, 'maximum': 600}})
    # metadata: {'type': 'integer', 'minimum': 100, 'maximum': 600, 'required': True}
    status: typing.Optional[str] = field(metadata={'openapi': {'readOnly': True}})
    # metadata: {'type': 'string', 'readOnly': True, 'required': False}
    statusCode: typing.Optional[int] = field(metadata={'openapi': {'minimum': 100, 'maximum': 600, 'deprecated': True}})
    # metadata: {'type': 'integer', 'minimum': 100, 'maximum': 600, 'deprecated': True, 'required': False}


# metadata: {'type': 'object'}
class Toplevel:
    errors: typing.Optional[typing.List[ErrorModel]] = field(metadata={'openapi': {'description': 'list of error model', 'minItems': 1, 'maxItems': 3}})
    # metadata: {'required': False, 'description': 'list of error model', 'type': 'array', 'minItems': 1, 'maxItems': 3}
    errors_inline: typing.Optional[typing.List[ErrorModel]] = field(metadata={ORIGINAL_NAME: 'errors-inline', 'openapi': {'minItems': 1, 'maxItems': 3}})
    # metadata: {'type': 'array', 'minItems': 1, 'maxItems': 3, 'required': False}
    date: typing.Optional[str] = field(metadata={'openapi': {'pattern': '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]?\\d{2}:\\d{2})'}})
    # metadata: {'required': False, 'type': 'string', 'pattern': '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]?\\d{2}:\\d{2})'}
    inline_date: typing.Optional[str] = field(metadata={ORIGINAL_NAME: 'inline-date', 'openapi': {'pattern': '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]?\\d{2}:\\d{2})'}})
    # metadata: {'type': 'string', 'pattern': '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]?\\d{2}:\\d{2})', 'required': False}
