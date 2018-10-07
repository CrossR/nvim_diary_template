
import unittest
from typing import Any, List

from .mocks.mock_github import get_mock_github
from .mocks.mock_nvim import MockNvim
from ..classes.nvim_github_class import SimpleNvimGithub
from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment


class SimpleNvimGithubTest(unittest.TestCase):
    """
    Tests for methods in the SimpleNvimGithub class.
    """

    def setUp(self) -> None:
        self.nvim: Any = MockNvim()
        api_setup = get_mock_github()

        self.api: Any = api_setup[0]
        self.options: Any = api_setup[1]

        self.github: SimpleNvimGithub = SimpleNvimGithub(
            self.nvim, self.options, self.api
        )

    def test_get_all_open_issues(self) -> None:
        issue_list: List[GitHubIssue] = [
            GitHubIssue(
                number=1,
                title="Test Issue",
                complete=False,
                labels=["backlog", "personal"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["This is the main issue body"],
                        tags=[],
                        updated_at="2018-01-01 10:00",
                    ),
                    GitHubIssueComment(
                        number=1,
                        body=["Line 1", "Line 2"],
                        tags=[],
                        updated_at="2018-08-19 19:18",
                    ),
                ],
                metadata=[],
            ),
            GitHubIssue(
                number=2,
                title="Test Issue 2",
                complete=False,
                labels=["inprogress", "work"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=[
                            "This is the second issue body:",
                            "    * Item 1",
                            "    * Item 2",
                        ],
                        tags=[],
                        updated_at="2018-01-01 10:00",
                    ),
                    GitHubIssueComment(
                        number=1,
                        body=["Line 1", "Line 2"],
                        tags=[],
                        updated_at="2018-08-19 19:18",
                    ),
                    GitHubIssueComment(
                        number=2,
                        body=["Line 2-1", "Line 2-2"],
                        tags=[],
                        updated_at="2018-08-19 13:18",
                    ),
                ],
                metadata=[],
            ),
        ]

        result: List[GitHubIssue] = self.github.get_all_open_issues()
        assert result == issue_list

    def test_filter_comments(self) -> None:
        self.github.issues[1].all_comments[2].tags = ["edit"]

        filtered_list: List[GitHubIssue] = [
            GitHubIssue(
                number=2,
                title="Test Issue 2",
                complete=False,
                labels=["inprogress", "work"],
                metadata=[],
                all_comments=[
                    GitHubIssueComment(
                        number=2,
                        body=["Line 2-1\r\nLine 2-2"],
                        tags=["edit"],
                        updated_at="2018-08-19 13:18",
                    )
                ],
            )
        ]

        change_list: List[Any] = [{"issue": 1, "comment": 2}]

        result: Any = SimpleNvimGithub.filter_comments(self.github.issues, "edit")
        assert result[0] == filtered_list
        assert result[1] == change_list

    def test_filter_issues(self) -> None:
        self.github.issues[1].metadata = ["edit"]

        filtered_list: List[GitHubIssue] = [
            GitHubIssue(
                number=2,
                title="Test Issue 2",
                complete=False,
                labels=["inprogress", "work"],
                metadata=["edit"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=[
                            "This is the second issue body:\r\n    * Item 1\r\n    * Item 2"
                        ],
                        tags=[],
                        updated_at="2018-08-19 19:18",
                    )
                ],
            )
        ]

        change_list: List[int] = [1]

        result: Any = SimpleNvimGithub.filter_issues(self.github.issues, "edit")
        assert result[0] == filtered_list
        assert result[1] == change_list
