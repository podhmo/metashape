from __future__ import annotations
import typing


# original is commit
class Commit:
    author: typing.Optional[CommitAuthor]
    commit: typing.Optional[CommitCommit]
    files: typing.Optional[typing.List[CommitFilesItem]]


# original is commitFilesItem
class CommitFilesItem:
    additions: typing.Optional[int]
    blob_url: typing.Optional[str]
    changes: typing.Optional[int]
    deletions: typing.Optional[int]
    filename: typing.Optional[str]
    patch: typing.Optional[str]
    raw_url: typing.Optional[str]
    status: typing.Optional[str]


# original is commitCommit
class CommitCommit:
    author: typing.Optional[CommitCommitAuthor]
    committer: typing.Optional[CommitCommitCommitter]
    message: typing.Optional[str]
    tree: typing.Optional[CommitCommitTree]
    url: typing.Optional[str]


# original is commitCommitTree
class CommitCommitTree:
    sha: typing.Optional[str]
    url: typing.Optional[str]


# original is commitCommitCommitter
class CommitCommitCommitter:
    date: typing.Optional[str]
    email: typing.Optional[str]
    name: typing.Optional[str]


# original is commitCommitAuthor
class CommitCommitAuthor:
    date: typing.Optional[str]
    email: typing.Optional[str]
    name: typing.Optional[str]


# original is commitAuthor
class CommitAuthor:
    avatar_url: typing.Optional[str]
    gravatar_id: typing.Optional[str]
    id: typing.Optional[int]
    login: typing.Optional[str]
    url: typing.Optional[str]
