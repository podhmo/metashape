from __future__ import annotations
import typing as t
import typing_extensions as tx
from metashape.declarative import field


class OpenAPIMetadata:
    def __init__(self, *, nullable: t.Optional[bool] = None):
        self.metadata = dict(nullable=nullable)

    def as_metadata(self) -> t.Dict[repr, t.Any]:
        return {"openapi": self.metadata}


class Data:
    name: str
    optional_name: t.Optional[str]

    nullable_name: str = field(metadata={"openapi": {"nullable": True}})
    optional_nullable_name: t.Optional[str] = field(
        metadata={"openapi": {"nullable": True}}
    )

    nullable_name2: tx.Annotated[str, OpenAPIMetadata(nullable=True)]
    optional_nullable_name2: tx.Annotated[
        t.Optional[str], OpenAPIMetadata(nullable=True)
    ]
