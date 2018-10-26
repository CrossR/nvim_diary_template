from __future__ import annotations

from datetime import datetime
from tempfile import mkdtemp
from typing import Any, List, Tuple

from dataclasses import dataclass
from dateutil import parser

from ...classes.github_issue_class import GitHubIssue
from ...utils.constants import ISO_FORMAT
from .mock_options import MockPluginOptions


def get_mock_github() -> Tuple[MockGitHubService, MockPluginOptions]:
    new_api: MockGitHubService = MockGitHubService()
    options: MockPluginOptions = MockPluginOptions()

    # Setup options
    options.config_path = mkdtemp()
    options.repo_name = "CrossR/nvim_diary_template"

    # Setup the GitHub Mock API
    new_api.repo.issues = [
        MockGitHubIssue(
            number=1,
            title="Test Issue",
            complete=False,
            labels=[MockGitHubLabel("backlog"), MockGitHubLabel("personal")],
            body="This is the main issue body",
            updated_at=parser.parse("2018-01-01 10:00"),
            comments=[
                MockGitHubComment(
                    number=0,
                    body="Line 1\nLine 2",
                    updated_at=parser.parse("2018-08-19 18:18"),
                )
            ],
        ),
        MockGitHubIssue(
            number=2,
            title="Test Issue 2",
            complete=False,
            labels=[MockGitHubLabel("inprogress"), MockGitHubLabel("work")],
            body="This is the second issue body:\n    * Item 1\n    * Item 2\n\n\n",
            updated_at=parser.parse("2018-01-01 10:00"),
            comments=[
                MockGitHubComment(
                    number=0,
                    body="Line 1\nLine 2",
                    updated_at=parser.parse("2018-08-19 18:18"),
                ),
                MockGitHubComment(
                    number=1,
                    body="\n\nLine 2-1\nLine 2-2",
                    updated_at=parser.parse("2018-08-19 12:18"),
                ),
            ],
        ),
    ]

    return new_api, options


class MockGitHubService:
    def __init__(self) -> None:
        self.active = True
        self.issues: List[GitHubIssue] = []
        self.repo: MockGitHubRepo = MockGitHubRepo()
        self.user: MockGitHubUser = MockGitHubUser([self.repo])

    def get_repo(self, name: str) -> MockGitHubRepo:
        return self.repo

    def get_user(self, name: str) -> MockGitHubUser:
        return self.user


class MockGitHubRepo:
    def __init__(self) -> None:
        self.full_name: str = ""
        self.labels: List[str] = []
        self.issues: List[MockGitHubIssue] = []

    def get_labels(self) -> List[str]:
        return self.labels

    def get_issues(self, state: str = "open") -> List[MockGitHubIssue]:
        return self.issues

    def get_issue(self, issue_number: int) -> MockGitHubIssue:
        return self.issues[issue_number - 1]

    def create_issue(self, title: str, body: str, labels: List[str]) -> MockGitHubIssue:
        new_issue: MockGitHubIssue = MockGitHubIssue()
        new_issue.number = len(self.issues) + 1
        new_issue.title = title
        new_issue.body = body
        new_issue.labels = [MockGitHubLabel(label) for label in labels]

        self.issues.append(new_issue)
        return new_issue


class MockGitHubIssue:
    def __init__(
        self,
        number: int = 0,
        title: str = "",
        complete: bool = False,
        body: str = "",
        labels: List[MockGitHubLabel] = [],
        comments: List[MockGitHubComment] = [],
        updated_at: datetime = parser.parse("2018-01-01 10:00"),
        state: str = "open",
    ) -> None:
        self.number: int = number
        self.title: str = title
        self.complete: bool = complete
        self.body: str = body
        self.labels: List[MockGitHubLabel] = labels
        self.comments: List[MockGitHubComment] = comments
        self.updated_at: datetime = updated_at
        self.state: str = state

    def get_comments(self) -> List[MockGitHubComment]:
        return self.comments

    def edit(
        self, body: str = "", title: str = "", labels: List[str] = [], state: str = ""
    ) -> None:
        if body != "":
            self.body = body

        if title != "":
            self.title = title

        if labels != []:
            self.labels = [MockGitHubLabel(label) for label in labels]

        if state != []:
            self.state = state

    def create_comment(self, body: str) -> MockGitHubComment:
        next_comment_number: int = 0

        if len(self.comments) != 0:
            next_comment_number = self.comments[-1].number + 1

        new_comment: MockGitHubComment = MockGitHubComment(
            number=next_comment_number, body=body, updated_at=datetime.now()
        )

        self.comments.append(new_comment)
        return new_comment


class MockGitHubComment:
    def __init__(
        self,
        number: int = 0,
        body: str = "",
        updated_at: datetime = parser.parse("2018-01-01 10:00"),
    ) -> None:
        self.number: int = number
        self.body: str = body
        self.updated_at: datetime = updated_at

    def edit(self, body: str) -> None:
        self.body = body


@dataclass
class MockGitHubUser:
    repos: List[MockGitHubRepo]


@dataclass
class MockGitHubLabel:
    name: str
