from __future__ import annotations
import typing as t
from ._typeinfo import (
    PrimitiveType,
    is_primitive_type,
    Atom,
    Container,
    TypeInfo,
    _default_raise_error,
)
from ._typeinfo_evil import typeinfo, omit_optional


__all__ = [
    "PrimitiveType",
    "is_primitive_type",
    "Atom",
    "Container",
    "TypeInfo",
    "_default_raise_error",
    "typeinfo",
    "omit_optional",
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
