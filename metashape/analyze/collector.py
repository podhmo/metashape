import typing as t
from .typeinfo import is_primitive_type, PrimitiveType

_Value = t.Union[t.List[t.Any], t.Dict[str, t.Any], t.Any]


class Collector:
    def __init__(
        self, fn: t.Callable[[t.Any], t.Union[t.List[t.Any], t.Dict[str, t.Any]]]
    ) -> None:
        self.fn = fn

    def collect(self, val: _Value) -> _Value:
        if isinstance(val, (list, tuple)):
            return self.collect_list(val)
        elif isinstance(val, dict):
            return self.collect_dict(val)
        elif is_primitive_type(val):
            return self.collect_primitive(val)  # type:ignore
        else:
            return self.fn(val)

    __call__ = collect

    def collect_list(self, val: t.List[t.Any]) -> _Value:
        return [self.collect(x) for x in val]

    def collect_dict(self, val: t.Dict[str, t.Any]) -> _Value:
        return {k: self.collect(v) for k, v in val.items()}

    def collect_primitive(self, val: PrimitiveType) -> _Value:
        return val
