import typing as t
import typing_extensions as tx


class Person:
    name: str
    age: int
    personality: tx.Literal["chaos", "neutral", "law"]
    gender: t.Optional[tx.Literal["F", "M"]]
