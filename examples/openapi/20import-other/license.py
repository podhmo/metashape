from __future__ import annotations
import typing as t
import typing_extensions as tx


class License:
    name: str
    type: LicenseType  # FIXME: use $ref
    message: t.Optional[str]


LicenseType = tx.Literal["mit", "gpl"]
