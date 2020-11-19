import typing as t
import sys
import re
from .types import T


# makedict
if sys.version_info[:2] >= (3, 6):
    make_dict = dict
else:
    from collections import OrderedDict as make_dict  # noqa

# get_args
typing_get_args = getattr(t, "get_args", None)
if typing_get_args is None:
    import typing_inspect as ti

    typing_get_args = ti.get_args


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
    ignore_rx: re.Pattern[str] = re.compile("[^0-9a-zA-Z_]+"),
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
