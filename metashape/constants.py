import typing as t

# keys ##############################
# original name (e.g. python's reserved word is used)
ORIGINAL_NAME = "original_name"

# types ##############################
# something like graphql schema's ID type
ID = t.NewType("ID", str)
