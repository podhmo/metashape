import typing as t

T = t.TypeVar("T")
ID = t.NewType("ID", str)
MetaData = t.Optional[t.Dict[str, t.Any]]

# TODO: more strict definition
IsMemberFunc = t.Callable[[t.Type[T]], bool]
EmitFunc = t.Callable[..., None]
