import typing as t
from dataclasses import MISSING  # noqa F401


# keys ##############################
# original name (e.g. python's reserved word is used)
ORIGINAL_NAME = "original_name"

# default value (e.g. 0, ""..  .etc)
DEFAULT = "default"

# types ##############################
# something like graphql schema's ID type
ID = t.NewType("ID", str)
