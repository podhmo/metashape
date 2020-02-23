from __future__ import annotations
import typing as t
import contextlib
from prestring import NEWLINE, Module as _Module


class Module(_Module):
    def sep(self) -> None:
        self.stmt("")

    @contextlib.contextmanager
    def block(self, value: t.Optional[t.Any] = None) -> t.Iterator[None]:
        if value is None:
            self.stmt("{")
        else:
            self.body.append(value)
            self.body.append(" {")
            self.body.append(NEWLINE)
        with self.scope():
            yield
        self.stmt("}")
