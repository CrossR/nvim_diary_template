from typing import Any, Dict, List, Optional

from ...classes.github_issue_class import GitHubIssue


class MockGitHubService:
    def __init__(self) -> None:
        self.active = True
        self.issues: List[GitHubIssue] = []
        self.repo: Optional[MockGitHubRepo] = None
        self.user: Optional[MockGitHubUser] = None

    def get_repo(self, name: str) -> MockGitHubRepo:
        if self.repo is not None:
            return self.repo
        else:
            return MockGitHubRepo()

    def get_user(self, name: str) -> MockGitHubUser:
        if self.user is not None:
            return self.user
        else:
            return MockGitHubUser()


class MockGitHubRepo:
    def __init__(self) -> None:
        self.full_name: str = ""
        self.labels: List[str] = []
        self.issues: List[MockGitHubIssue] = []

    def get_labels(self) -> List[str]:
        return self.labels

    def get_issues(self) -> List[MockGitHubIssue]:
        return self.issues

    def create_issue(self, title: str, body: List[str], labels: List[str]) -> None:
        new_issue: MockGitHubIssue = MockGitHubIssue()
        new_issue.title = title
        new_issue.body = body
        new_issue.labels = labels


class MockGitHubIssue:
    def __init__(self) -> None:
        self.number: int = 0
        self.title: str = ""
        self.body: List[str] = []
        self.labels: List[str] = []
        self.comments: List[MockGitHubComment]
        self.updated_at: str = "2018-01-01 10:00"

    def get_comments(self) -> List[MockGitHubComment]:
        return self.comments

    def create_comment(self, body: List[str]) -> None:
        new_comment: MockGitHubComment = MockGitHubComment()
        new_comment.body = body

        self.comments.append(new_comment)


class MockGitHubComment:
    def __init__(self) -> None:
        self.number: int = 0
        self.body: List[str] = []
        self.updated_at: str = "2018-01-01 12:00"


class MockGitHubUser:
    def __init__(self) -> None:
        self.repos: List[MockGitHubRepo] = []
