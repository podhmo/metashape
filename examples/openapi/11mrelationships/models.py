from __future__ import annotations
import typing as t


# from: https://docs.ponyorm.org/relationships.html
# multiple relationships between two entities
class User:
    name: str
    tweets: t.Set[Tweet]  # reverse: author
    favorites: t.Set[Tweet]  # reverse: favorited


class Tweet:
    text: str
    author: User  # reverse tweets
    favorited: t.Set[User]  # reverse favorites
