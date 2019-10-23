from __future__ import annotations
import typing as t
import typing_extensions as tx


class Todo:
    id: str
    kind: Kind
    kind2: tx.Literal["epic", "story", "task"]
    name: str
    description: t.Optional[str]
    priority: t.Optional[int]


Kind = tx.Literal["epic", "story", "task"]
