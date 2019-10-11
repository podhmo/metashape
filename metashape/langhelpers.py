import sys
from dictknife.langhelpers import reify  # noqa

if sys.version_info[:2] >= (3, 6):
    make_dict = dict
else:
    from collections import OrderedDict as make_dict  # noqa
