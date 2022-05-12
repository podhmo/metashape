from __future__ import annotations
import typing as t
import re
from .types import T


# makedict
make_dict = dict

# get_args
typing_get_args = t.get_args


# stolen from pyramid
class reify(t.Generic[T]):
    """cached property"""

    def __init__(self, wrapped: t.Callable[[t.Any], T]):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # noqa
            pass

    def __get__(
        self, inst: t.Optional[object], objtype: t.Optional[t.Type[t.Any]] = None
    ) -> T:
        if inst is None:
            return self  # type: ignore
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


# langhelpers
_NORMALIZE_ID_DICT: t.Dict[str, t.Dict[str, str]] = {}


def normalize(
    name: str,
    ignore_rx: t.Pattern[str] = re.compile("[^0-9a-zA-Z_]+"),
    *,
    _id_dict_dict: t.Dict[str, t.Dict[str, str]] = _NORMALIZE_ID_DICT,
) -> str:
    c = name[0]
    if c.isdigit():
        name = "n" + name
    elif not (c.isalpha() or c == "_"):
        name = "_invalid_" + name
    normalized_name = ignore_rx.sub("", name.replace("-", "_"))

    _id_dict = _id_dict_dict.get(normalized_name)
    if _id_dict is None:
        _id_dict = _id_dict_dict[normalized_name] = {name: normalized_name}
        return normalized_name
    uid = _id_dict.get(name)
    if uid is None:
        uid = _id_dict[name] = normalized_name + "G" + str(len(_id_dict))
    return uid


def titleize(name: str) -> str:
    if not name:
        return name
    name = str(name)
    return normalize("{}{}".format(name[0].upper(), name[1:]))
