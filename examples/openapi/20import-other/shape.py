import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.absolute()))
from users import UserList  # noqa
from info import Info  # noqa


class Toplevel:
    info: Info
    users: UserList
