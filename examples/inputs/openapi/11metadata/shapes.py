from __future__ import annotations
import typing
from metadata.declarative import (
    field,
    ORIGINAL_NAME,
)


# metadata: {'description': 'this is error model', 'type': 'object'}
class ErrorModel:
    """
    this is error model
    """

    message: str
    # metadata: {'type': 'string', 'required': True}
    code: int
    # metadata: {'type': 'integer', 'minimum': 100, 'maximum': 600, 'required': True}
    status: typing.Optional[str]
    # metadata: {'type': 'string', 'readOnly': True, 'required': False}
    statusCode: typing.Optional[int]
    # metadata: {'type': 'integer', 'minimum': 100, 'maximum': 600, 'deprecated': True, 'required': False}


# metadata: {'type': 'object'}
class Toplevel:
    errors: typing.Optional[typing.List[ErrorModel]]
    # metadata: {'required': False, 'description': 'list of error model', 'type': 'array', 'minItems': 1, 'maxItems': 3}
    errors_inline: typing.Optional[typing.List[ErrorModel]] = field(metadata={ORIGINAL_NAME: 'errors-inline'})
    # metadata: {'type': 'array', 'minItems': 1, 'maxItems': 3, 'required': False}
