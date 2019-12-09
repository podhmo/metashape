import contextlib
from prestring import NEWLINE, Module as _Module


class Module(_Module):
    def sep(self):
        self.stmt("")

    @contextlib.contextmanager
    def block(self, value=None, *, surround=True):
        if value is None:
            self.stmt("{")
        else:
            self.body.append(value)
            self.body.append(" {")
            self.body.append(NEWLINE)
        with self.scope():
            yield
        self.stmt("}")
