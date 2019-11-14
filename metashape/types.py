import typing as t
import typing_extensions as tx
from .constants import ID  # noqa F401

T = t.TypeVar("T")

Kind = tx.Literal["object", "enum", "ignore"]
MetaData = t.Optional[t.Dict[str, t.Any]]

# TODO: more strict typing
Member = t.Type[t.Any]
IsMemberFunc = t.Callable[[t.Type[t.Any]], bool]
GuessMemberFunc = t.Callable[[t.Type[t.Any]], t.Optional[Kind]]
EmitFunc = t.Callable[..., None]


class _ForwardRef(tx.Protocol):
    @property
    def __forward_arg__(self) -> str:
        ...
