from typing import List

from ...classes.github_issue_class import GitHubIssue


class MockGitHubService:
    def __init__(self) -> None:
        self.active = True
        self.issues: List[GitHubIssue] = []
