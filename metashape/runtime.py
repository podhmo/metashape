import typing as t
import typing_extensions as tx
import sys
import logging
import inspect
import types
from metashape.marker import mark, is_marked, guess_mark
from metashape.types import Kind, Member, GuessMemberFunc
from metashape.analyze.resolver import Resolver
from metashape.analyze.walker import Walker
from metashape.analyze.config import Config
from metashape.analyze import typeinfo  # TODO: remove
from ._access import get_name

logger = logging.getLogger(__name__)


def get_walker(
    target: t.Union[
        None,
        types.ModuleType,
        t.Type[t.Any],
        t.List[t.Type[t.Any]],
        t.Dict[str, t.Type[t.Any]],
    ] = None,
    *,
    config: t.Optional[Config] = None,
    aggressive: bool = False,
    only: t.Optional[t.List[str]] = None,
    _depth: int = 1,  # xxx: for black magic
) -> Walker:
    config = config or Config()
    resolver = Resolver()

    if target is None:
        if aggressive:
            logger.info(
                "aggressive=True and target=None, guessing target module... this is unsafe action"
            )
            # xxx: extract caller module (black magic)
            frame = sys._getframe(_depth)
            here = frame.f_globals["__name__"]
            try:
                target = sys.modules[here]
            except KeyError:
                raise ValueError("supported only module name")

    if target is None:
        raise ValueError("support target=None, only aggresive=True")
    elif isinstance(target, types.ModuleType):
        d = target.__dict__
        if aggressive and only is None:
            only = [target.__name__]
    elif isinstance(target, dict):
        d = target
    elif isinstance(target, (list, tuple)):
        d = {x.__name__: x for x in target}
        for x in target:
            mark(x, kind=_guess_kind(x) or "object")
    else:
        d = {get_name(target): target}
        mark(target, kind=_guess_kind(target) or "object")

    if only is not None:
        d = {
            k: v
            for k, v in d.items()
            if getattr(v, "__module__", "") in only or hasattr(v, "__origin__")
        }  # xxx: for supporting enum, see __origin__

    if aggressive:
        for name, v in list(d.items()):
            kind = _guess_kind(v)
            if kind is not None:
                if kind == "enum":
                    v.__name__ = name  # xxx TODO: use tx.Annotated
                mark(v, kind=kind)

    recursive = config.option.recursive
    sort = config.option.sort

    itr = sorted(d.items()) if sort else d.items()
    members = [v for _, v in itr if is_marked(v)]

    w = Walker(members, resolver=resolver, config=config)

    if recursive:
        if aggressive:
            guess_member = _guess_kind
        else:
            guess_member = guess_mark
        w._members = list(
            _mark_recursive(w, w._members, seen=set(), guess_member=guess_member)
        )  # xxx:
    return w


# TODO: move to walker's code
def _mark_recursive(
    w: Walker,
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

        for _, info, _ in w.for_type(m).walk():
            if info.normalized in seen:
                continue

            for x in typeinfo.get_args(info) or [info]:
                if x.normalized in seen:
                    continue

                kind = guess_member(x.normalized)
                if kind is None:
                    continue

                mark(x.normalized, kind=kind)
                yield x.normalized
                q.append(x.normalized)


def _guess_kind(cls: t.Type[t.Any]) -> t.Optional[Kind]:
    # is custom class?
    if hasattr(cls, "__name__"):
        if not hasattr(cls, "__loader__") and hasattr(cls, "__annotations__"):
            if not inspect.isclass(cls):
                return None
            return "object"
        return None

    # is tx.Literal?
    if hasattr(cls, "__origin__") and cls.__origin__ is tx.Literal:
        return "enum"

    return None
