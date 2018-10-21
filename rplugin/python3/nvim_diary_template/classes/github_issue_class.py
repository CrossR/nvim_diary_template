# pylint: disable=all
"""github_issue_class

A simple Dataclass to store GitHub issues.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class GitHubIssueComment:
    """GitHubIssueComment

    A simple Dataclass to store a GitHub issues comment.
    """

    number: int
    body: List[str]
    tags: List[str]
    updated_at: str


@dataclass
class GitHubIssue:
    """GitHubIssue

    A simple Dataclass to store a GitHub issue.
    """

    number: int
    title: str
    complete: bool
    labels: List[str]
    all_comments: List[GitHubIssueComment]
    metadata: List[str]
