from json_to_models.dynamic_typing import IntString
from typing import Any, List


class Data0:
    id: IntString
    type: str
    actor: 'Actor'
    repo: 'Repo'
    payload: 'Payload'
    public: bool
    created_at: str


class Actor:
    id: int
    login: str
    display_login: str
    gravatar_id: str
    url: str
    avatar_url: str


class Repo:
    id: int
    name: str
    url: str


class Payload:
    action: str
    number: int
    pull_request: 'PullRequest'


class PullRequest:
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: 'Owner_User'
    body: str
    created_at: str
    updated_at: str
    closed_at: None
    merged_at: None
    merge_commit_sha: None
    assignee: None
    assignees: List[Any]
    requested_reviewers: List[Any]
    requested_teams: List[Any]
    labels: List[Any]
    milestone: None
    commits_url: str
    review_comments_url: str
    review_comment_url: str
    comments_url: str
    statuses_url: str
    head: 'Base_Head'
    base: 'Base_Head'
    _links: '_link'
    author_association: str
    merged: bool
    mergeable: None
    rebaseable: None
    mergeable_state: str
    merged_by: None
    comments: int
    review_comments: int
    maintainer_can_modify: bool
    commits: int
    additions: int
    deletions: int
    changed_files: int


class _link:
    self: 'Comment_Commit_Html_Issue_Self_Status'
    html: 'Comment_Commit_Html_Issue_Self_Status'
    issue: 'Comment_Commit_Html_Issue_Self_Status'
    comments: 'Comment_Commit_Html_Issue_Self_Status'
    review_comments: 'Comment_Commit_Html_Issue_Self_Status'
    review_comment: 'Comment_Commit_Html_Issue_Self_Status'
    commits: 'Comment_Commit_Html_Issue_Self_Status'
    statuses: 'Comment_Commit_Html_Issue_Self_Status'


class Owner_User:
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class Base_Head:
    label: str
    ref: str
    sha: str
    user: 'Owner_User'
    repo: 'Repo_1Z'


class Comment_Commit_Html_Issue_Self_Status:
    href: str


class Repo_1Z:
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: 'Owner_User'
    html_url: str
    description: str
    fork: bool
    url: str
    forks_url: str
    keys_url: str
    collaborators_url: str
    teams_url: str
    hooks_url: str
    issue_events_url: str
    events_url: str
    assignees_url: str
    branches_url: str
    tags_url: str
    blobs_url: str
    git_tags_url: str
    git_refs_url: str
    trees_url: str
    statuses_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    commits_url: str
    git_commits_url: str
    comments_url: str
    issue_comment_url: str
    contents_url: str
    compare_url: str
    merges_url: str
    archive_url: str
    downloads_url: str
    issues_url: str
    pulls_url: str
    milestones_url: str
    notifications_url: str
    labels_url: str
    releases_url: str
    deployments_url: str
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: str
    size: int
    stargazers_count: int
    watchers_count: int
    language: str
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    forks_count: int
    mirror_url: None
    archived: bool
    disabled: bool
    open_issues_count: int
    license: None
    forks: int
    open_issues: int
    watchers: int
    default_branch: str


