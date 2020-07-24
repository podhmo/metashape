import typing as t
import typing_extensions as tx
import sys
import logging
import inspect
import types
from metashape.marker import mark, is_marked, guess_mark
from metashape.types import Kind, Member, GuessMemberFunc
from metashape.typeinfo import typeinfo
from metashape.analyze.resolver import Resolver
from metashape.analyze.walker import Walker
from metashape.analyze.config import Config
from ._access import get_name, get_fullname  # noqa:F401

logger = logging.getLogger(__name__)
builtins = sys.modules["builtins"]


def _guess_kind(cls: t.Any) -> t.Optional[Kind]:
    # is module?
    if hasattr(cls, "__loader__"):
        return None

    # is typed user_defined_type class or callable?
    if hasattr(cls, "__name__") and hasattr(cls, "__annotations__"):
        if not callable(cls):
            return None
        if inspect.isclass(cls):
            return "object"
        return "callable"

    # is tx.Literal?
    if hasattr(cls, "__origin__") and cls.__origin__ is tx.Literal:
        return "enum"

    return None


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
    recursive: bool = False,
    sort: bool = False,
    only: t.Optional[t.List[str]] = None,
    _depth: int = 1,  # xxx: for black magic
    _extra_target_name: str = "__ADDITIONAL_TARGETS__",
    _seen_modules: t.Optional[t.Set[types.ModuleType]] = None,
    _guess_kind: t.Callable[[t.Any], t.Optional[Kind]] = _guess_kind,
) -> Walker:
    if _seen_modules is None:
        _seen_modules = set()

    config = config or Config()

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
        _seen_modules.add(target)
        d = target.__dict__
        if aggressive and only is None:
            only = [get_name(target)]

    elif isinstance(target, dict):
        d = target
        for x in d.values():
            mark(x, kind=_guess_kind(x) or "object")
    elif isinstance(target, (list, tuple)):
        d = {get_name(x): x for x in target}
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

    recursive = recursive or config.option.recursive
    sort = sort or config.option.sort

    itr = sorted(d.items()) if sort else d.items()
    members = [
        (typeinfo(v).user_defined_type or v if hasattr(v, "__origin__") else v)
        for _, v in itr
        if is_marked(v)
    ]

    named = {id(val): name for name, val in d.items()}
    resolver = Resolver(config=config, named=named)
    w = Walker(members, resolver=resolver, config=config)

    if recursive:
        if aggressive:
            guess_member = _guess_kind
        else:
            guess_member = guess_mark
        w._members = list(
            _mark_recursive(w, w._members, seen=set(), guess_member=guess_member)
        )  # xxx:

    if isinstance(target, types.ModuleType):
        for x in getattr(target, _extra_target_name, None) or []:
            if isinstance(x, types.ModuleType):
                _seen_modules.add(x)
                sw = get_walker(
                    x,
                    config=config,
                    aggressive=aggressive,
                    recursive=recursive,
                    sort=sort,
                    only=None,
                    _depth=_depth + 1,
                    _extra_target_name=_extra_target_name,
                    _seen_modules=_seen_modules,
                    _guess_kind=_guess_kind,
                )
                w._members.extend(sw._members)
            else:
                mark(x, kind=_guess_kind(x) or "object")
                w._members.append(x)

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

        for _, info, _ in w.walk_fields(m):
            if info.type_ in seen:
                continue

            for x in info.args or [info]:
                if x.type_ in seen:
                    continue

                kind = guess_member(x.type_)
                if kind is None:
                    continue

                mark(x.type_, kind=kind)
                yield x.type_
                q.append(x.type_)
