from __future__ import annotations
import typing as t


class Team:
    name: str
    members: t.List[Member]


class Member:
    name: str
    team: Team


def walk(w):
    defs = {}
    for cls in w.walk():
        defs[cls.__name__] = {
            name: str(typeinfo.raw) for name, typeinfo, _ in w.walk_fields(cls)
        }
    return defs


if __name__ == "__main__":
    import json
    from metashape import runtime

    print(
        json.dumps(
            {
                "one": walk(runtime.get_walker(Team)),
                "list": walk(runtime.get_walker([Team, Member])),
                "with-recursive": walk(
                    runtime.get_walker(
                        [Team],
                        config=runtime.Config(
                            option=runtime.Config.Option(recursive=True)
                        ),
                    )
                ),
            },
            indent=2,
        )
    )
