import typing as t
import typing_extensions as tx
from metashape.marker import mark, is_marked, guess_mark
from metashape.types import Kind, Member, GuessMemberFunc
from metashape.analyze.resolver import Resolver
from metashape.analyze.walker import ModuleWalker
from metashape.analyze import typeinfo  # TODO: remove


def get_walker(
    target: t.Union[t.Type[t.Any], t.List[t.Type[t.Any]], t.Dict[str, t.Type[t.Any]]],
    *,
    aggressive: bool = False,
    recursive: bool = False,
    sort: bool = False,
) -> ModuleWalker:
    if isinstance(target, dict):
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
    w = ModuleWalker(members, resolver=Resolver())
    if recursive:
        if aggressive:
            guess_member = _guess_kind_aggressive
        else:
            guess_member = guess_mark
        w._members = list(
            _mark_recursive(w, w._members, seen=set(), guess_member=guess_member)
        )  # xxx:
    return w


# TODO: move to walker's code
def _mark_recursive(
    w: ModuleWalker,
    members: t.List[Member],
    *,
    seen: t.Set[t.Type[t.Any]],
    guess_member: GuessMemberFunc,
) -> t.Iterable[t.Type[t.Any]]:
    from collections import deque

    q: t.Deque[t.Type[t.Any]] = deque()
    for m in members:
        q.append(m)

    while True:
        try:
            m = q.popleft()
        except IndexError:
            break
        if m in seen:
            continue
        seen.add(m)
        yield m

        for _, typ, _ in w.for_type(m).walk():
            if typ in seen:
                continue

            info = w.resolver.resolve_type_info(typ)
            if info.normalized in seen:
                continue

            args = typeinfo.get_args(info)  # xxx
            if not args:
                kind = guess_member(info.normalized)
                if kind is not None:
                    mark(info.normalized, kind=kind)
                    yield info.normalized
                    q.append(info.normalized)
                continue

            for x in args:
                if x.normalized in seen:
                    continue
                kind = guess_member(x.normalized)
                if kind is not None:
                    mark(x.normalized, kind=kind)
                    yield x.normalized
                    q.append(x.normalized)

def _guess_kind_aggressive(cls: t.Type[t.Any]) -> t.Optional[Kind]:
    # is custom class?
    if hasattr(cls, "__name__"):
        if not hasattr(cls, "__loader__") and hasattr(cls, "__annotations__"):
            return "object"
        else:
            return None

    # is tx.Literal?
    if hasattr(cls, "__origin__") and cls.__origin__ is tx.Literal:
        return "enum"

    return None
