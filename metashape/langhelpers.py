import sys

# util
if (sys.version_info[0], sys.version_info[1]) >= (3, 7):
    make_dict = dict
else:
    from collections import OrderedDict as make_dict  # noqa
