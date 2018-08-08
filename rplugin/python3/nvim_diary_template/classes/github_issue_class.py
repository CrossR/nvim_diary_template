"""github_issue_class

A simple Dataclass to store GitHub issues.
"""
from dataclasses import dataclass


@dataclass
class GitHubIssue:
    """GitHubIssue

    A simple Dataclass to store a GitHub issue.
    """

    number: int
    title: str
    complete: bool
    labels: list
    all_comments: list
    metadata: list


@dataclass
class GitHubIssueComment:
    """GitHubIssueComment

    A simple Dataclass to store a GitHub issues comment.
    """

    number: int
    body: list
    tags: list
    updated_at: str
