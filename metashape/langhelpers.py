import typing as t
import sys
from .types import T


if sys.version_info[:2] >= (3, 6):
    make_dict = dict
else:
    from collections import OrderedDict as make_dict  # noqa


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
