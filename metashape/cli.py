import typing as t
from metashape import T
from metashape import FakeResolver, Accessor, translate


def run(
    filename: str,
    *,
    aggressive: bool = False,
    is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
) -> None:
    from magicalimport import import_module  # type:ignore

    m = import_module(filename)
    if aggressive:
        is_member = lambda x: hasattr(x, "__name__")  # noqa

    resolver = FakeResolver(is_member=is_member)
    accessor = Accessor(
        resolver=resolver, repository=resolver.resolve_repository(m.__dict__)
    )
    print(translate(accessor))


def main(*, argv: t.Optional[t.List[str]] = None) -> None:
    import argparse
    import logging

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help  # type:ignore
    parser.add_argument("filename")
    parser.add_argument("--aggressive", action="store_true")
    parser.add_argument(
        "--logging", choices=list(logging._nameToLevel.keys()), default="DEBUG"
    )
    args = parser.parse_args(argv)

    params = vars(args)
    logging.basicConfig(level=params.pop("logging"))
    run(**params)
