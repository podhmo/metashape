import typing as t
import typing_extensions as tx

T = t.TypeVar("T")

Kind = tx.Literal["object", "enum"]
MetaData = t.Optional[t.Dict[str, t.Any]]

ID = t.NewType("ID", str)  # TODO: move?

# TODO: more strict definition
Member = t.Type[t.Any]
IsMemberFunc = t.Callable[[t.Type[t.Any]], bool]
GuessMemberFunc = t.Callable[[t.Type[t.Any]], t.Optional[Kind]]


class _ForwardRef(tx.Protocol):
    @property
    def __forward_arg__(self) -> str:
        ...


EmitFunc = t.Callable[..., None]
