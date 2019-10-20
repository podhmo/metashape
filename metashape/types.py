import typing as t

T = t.TypeVar("T")

MetaData = t.Optional[t.Dict[str, t.Any]]

# TODO: more strict definition
IsMemberFunc = t.Callable[[t.Type[T]], bool]
EmitFunc = t.Callable[..., None]
