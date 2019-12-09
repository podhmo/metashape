import typing as t
import typing_extensions as tx
from collections import namedtuple
from .typeinfo import is_primitive_type, PrimitiveType

_Value = t.Union[t.List[t.Any], t.Dict[str, t.Any], t.Any]
_Context = namedtuple("_Context", "args, kwargs")


class CollectFunction(tx.Protocol):
    def __call__(self, val: _Value, *args: t.Any, **kwargs: t.Any) -> _Value:
        ...


class Collector:
    def __init__(self, fn: CollectFunction) -> None:
        self.fn = fn

    def __call__(self, val: _Value, *args: t.Any, **kwargs: t.Any) -> _Value:
        return self.collect(_Context(args=args, kwargs=kwargs), val)

    def collect(self, ctx: _Context, val: _Value) -> _Value:
        if isinstance(val, (list, tuple)):
            return self.collect_list(ctx, val)
        elif isinstance(val, dict):
            return self.collect_dict(ctx, val)
        elif is_primitive_type(val):
            return self.collect_primitive(ctx, val)
        else:
            return self.fn(val, *ctx.args, **ctx.kwargs)

    def collect_list(self, ctx: _Context, val: t.Sequence[t.Any]) -> _Value:
        return [self.collect(ctx, x) for x in val]

    def collect_dict(self, ctx: _Context, val: t.Dict[str, t.Any]) -> _Value:
        return {k: self.collect(ctx, v) for k, v in val.items()}

    def collect_primitive(self, ctx: _Context, val: PrimitiveType) -> _Value:
        return val
