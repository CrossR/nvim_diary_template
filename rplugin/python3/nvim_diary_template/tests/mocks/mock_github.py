from datetime import datetime
from tempfile import mkdtemp
from typing import Any, Dict, List

from dataclasses import dataclass
from dateutil import parser
from neovim import Nvim

from ...classes.github_issue_class import GitHubIssue
from ...classes.nvim_github_class import SimpleNvimGithub
from ...utils.constants import ISO_FORMAT
from .mock_options import MockPluginOptions


def get_mock_github(nvim: Nvim) -> SimpleNvimGithub:
    new_api: Any = MockGitHubService()
    options: Any = MockPluginOptions()

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

    nvim_github: SimpleNvimGithub = SimpleNvimGithub(nvim, options, new_api)
    return nvim_github


# TODO: Fix these forward type references to not be Any.
class MockGitHubService:
    def __init__(self) -> None:
        self.active = True
        self.issues: List[GitHubIssue] = []
        self.repo: MockGitHubRepo = MockGitHubRepo()
        self.user: MockGitHubUser = MockGitHubUser([self.repo])

    def get_repo(self, name: str) -> Any:
        return self.repo

    def get_user(self, name: str) -> Any:
        return self.user


class MockGitHubRepo:
    def __init__(self) -> None:
        self.full_name: str = ""
        self.labels: List[str] = []
        self.issues: List[MockGitHubIssue] = []

    def get_labels(self) -> List[str]:
        return self.labels

    def get_issues(self, state: str = "open") -> List[Any]:
        return self.issues

    def create_issue(self, title: str, body: str, labels: List[str]) -> None:
        new_issue: MockGitHubIssue = MockGitHubIssue()
        new_issue.title = title
        new_issue.body = body
        new_issue.labels = [MockGitHubLabel(label) for label in labels]


class MockGitHubIssue:
    def __init__(
        self,
        number: int = 0,
        title: str = "",
        complete: bool = False,
        body: str = "",
        labels: List[Any] = [],
        comments: List[Any] = [],
        updated_at: datetime = parser.parse("2018-01-01 10:00"),
    ) -> None:
        self.number: int = number
        self.title: str = title
        self.complete: bool = complete
        self.body: str = body
        self.labels: List[MockGitHubLabel] = labels
        self.comments: List[MockGitHubComment] = comments
        self.updated_at: datetime = updated_at

    def get_comments(self) -> List[Any]:
        return self.comments

    def create_comment(self, body: str) -> None:
        new_comment: MockGitHubComment = MockGitHubComment()
        new_comment.body = body

        self.comments.append(new_comment)


@dataclass
class MockGitHubComment:
    number: int
    body: str
    updated_at: datetime


@dataclass
class MockGitHubUser:
    repos: List[MockGitHubRepo]


@dataclass
class MockGitHubLabel:
    name: str
