# type:ignore
from __future__ import annotations
import typing as t
from metashape.runtime import get_walker


class Team:
    name: str
    members: t.List[Member]


class Member:
    name: str
    team: Team


def _walk(w):
    defs = {}
    for cls in w.walk():
        if hasattr(cls, "__origin__") and cls.__origin__ == t.Union:  # xxx:
            w.append(cls)
            continue
        defs[cls.__name__] = {
            name: str(typeinfo.raw) for name, typeinfo, _ in w.walk_fields(cls)
        }
    return defs


def test_walk_one():
    got = _walk(get_walker(Team))
    want = {"Team": {"name": str(str), "members": str(t.List[Member])}}
    assert want == got


def test_walk_list():
    got = _walk(get_walker([Team, Member]))
    want = {
        "Team": {"name": str(str), "members": str(t.List[Member])},
        "Member": {"name": str(str), "team": str(Team)},
    }
    assert want == got


def test_walk_one__with_recursive():
    got = _walk(get_walker(Team, recursive=True))
    want = {
        "Team": {"name": str(str), "members": str(t.List[Member])},
        "Member": {"name": str(str), "team": str(Team)},
    }
    assert want == got


def test_walk_one__with_recursive2():
    got = _walk(get_walker(Member, recursive=True))
    want = {
        "Team": {"name": str(str), "members": str(t.List[Member])},
        "Member": {"name": str(str), "team": str(Team)},
    }
    assert want == got


def test_walk_one__container():
    got = _walk(get_walker(t.List[Member]))
    want = {
        "Member": {"name": str(str), "team": str(Team)},
    }
    assert want == got


def test_walk_one__union():
    from metashape.name import NewNamedType

    got = _walk(get_walker(NewNamedType("MemberOrTeam", t.Union[Member, Team])))
    want = {
        "Member": {"name": str(str), "team": str(Team)},
        "Team": {"name": str(str), "members": str(t.List[Member])},
    }
    assert want == got
