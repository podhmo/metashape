from __future__ import annotations
import typing as t
from ._typeinfo import (
    PrimitiveType,
    is_primitive_type,
    Atom,
    Container,
    Container_with_children,
    TypeInfo,
    _default_raise_error,
)
from ._typeinfo_evil import typeinfo, omit_optional
from ._typeinfo_typestring import type_string
from ._typeinfo_typestring import typeinfo_string as to_string

__all__ = [
    # exported functions (or classes)
    "typeinfo",
    "type_string",
    "to_string",
    "omit_optional",  # TODO: remove
    "is_primitive_type",
    "TypeInfo",
    # helpers
    "PrimitiveType",
    "Atom",
    "Container",
    "Container_with_children",
    "_default_raise_error",
]

if __name__ == "__main__":

    def main(argv: t.Optional[t.List[str]] = None) -> None:
        def run(path: str) -> None:
            from pprint import pprint
            from magicalimport import import_symbol

            x = import_symbol(path, cwd=True)
            pprint(typeinfo(x))

        import argparse

        parser = argparse.ArgumentParser(description=None)
        parser.print_usage = parser.print_help  # type: ignore
        parser.add_argument("path", help="<module>:<name>")
        args = parser.parse_args(argv)
        run(**vars(args))

    main()
