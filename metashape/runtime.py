import typing as t
import typing_extensions as tx
from metashape.marker import mark, is_marked
from metashape.types import Kind
from metashape.analyze.resolver import Resolver
from metashape.analyze.walker import ModuleWalker


def get_walker(
    target: t.Union[t.Type[t.Any], t.List[t.Type[t.Any]], t.Dict[str, t.Type[t.Any]]],
    *,
    aggressive: bool = False,
    sort: bool = False
) -> ModuleWalker:
    if hasattr(target, "items"):
        d = target
    elif isinstance(target, (list, tuple)):
        d = {x.__name__: x for x in target}
    else:
        d = {target.__name__: target}

    if aggressive:
        for name, v in list(d.items()):
            kind = _guess_kind_aggressive(v)
            if kind is not None:
                if kind == "enum":
                    v.__name__ = name  # xxx TODO: use tx.Annotated
                mark(v, kind=kind)

    itr = sorted(d.items()) if sort else d.items()
    members = [v for _, v in itr if is_marked(v)]
    return ModuleWalker(members, resolver=Resolver())


def _guess_kind_aggressive(x: t.Type[t.Any]) -> t.Optional[Kind]:
    # is custom class?
    if hasattr(x, "__name__"):
        if not hasattr(x, "__loader__") and hasattr(x, "__annotations__"):
            return "object"
        else:
            return None

    # is tx.Literal?
    if hasattr(x, "__origin__") and x.__origin__ is tx.Literal:
        return "enum"

    return None
