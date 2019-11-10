import unittest
from typing import Any, List

from dateutil import parser

from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..classes.nvim_github_class import SimpleNvimGithub
from ..classes.plugin_options import PluginOptions
from .mocks.mock_github import MockGitHubComment, MockGitHubService, get_mock_github
from .mocks.mock_nvim import MockNvim


class SimpleNvimGithubTest(unittest.TestCase):
    """
    Tests for methods in the SimpleNvimGithub class.
    """

    def setUp(self) -> None:
        self.nvim: MockNvim = MockNvim()
        api_setup = get_mock_github()

        self.api: MockGitHubService = api_setup[0]
        self.options: PluginOptions = api_setup[1]

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

        result = self.github.active_issues
        assert result == issue_list

    def test_filter_comments(self) -> None:
        self.github.active_issues[1].all_comments[2].tags = ["edit"]

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
        self.github.active_issues[1].metadata = ["edit"]

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

    def test_upload_comments(self) -> None:
        issue_list: List[GitHubIssue] = [
            GitHubIssue(
                number=0,
                title="",
                complete=False,
                labels=[],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["This is the main issue body"],
                        tags=[],
                        updated_at="2018-08-19 18:18",
                    ),
                    GitHubIssueComment(
                        number=1, body=[], tags=["new"], updated_at="0000-00-00 00:00"
                    ),
                ],
                metadata=[],
            )
        ]

        # Check the service is checked before being used.
        self.github.repo_name = ""
        assert self.nvim.message_print_count == 0
        self.github.upload_comments(issue_list, "new")
        assert self.nvim.message_print_count == 1

        self.github.repo_name = "CrossR/nvim_diary_template"
        self.nvim.message_print_count = 0
        self.nvim.errors = []

        # Check the number of comments doesn't change when the comment is
        # incomplete.
        assert len(self.api.repo.issues[0].comments) == 1
        self.github.upload_comments(issue_list, "new")
        assert len(self.api.repo.issues[0].comments) == 1

        issue_list[0].all_comments[1].body = ["New Line 1", "Newer Line 2"]

        # Check the number of comments increases and that the
        # new comment is correct.
        assert len(self.api.repo.issues[1].comments) == 2
        self.github.upload_comments(issue_list, "new")
        assert len(self.api.repo.issues[1].comments) == 3

        assert self.api.repo.issues[1].comments[2].number == 2
        assert self.api.repo.issues[1].comments[2].body == "New Line 1\r\nNewer Line 2"

    def test_upload_issues(self) -> None:
        issue_list: List[GitHubIssue] = [
            GitHubIssue(
                number=0,
                title="",
                complete=False,
                labels=[],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["Line 1", "Line 2"],
                        tags=[],
                        updated_at="0000-00-00 00:00",
                    )
                ],
                metadata=["new"],
            )
        ]

        # Check the service is checked before being used.
        self.github.repo_name = ""
        assert self.nvim.message_print_count == 0
        self.github.upload_issues(issue_list, "new")
        assert self.nvim.message_print_count == 1

        self.github.repo_name = "CrossR/nvim_diary_template"
        self.nvim.message_print_count = 0
        self.nvim.errors = []

        # Check the number of issues doesn't change when the issue is
        # incomplete.
        assert len(self.api.repo.issues) == 2
        self.github.upload_issues(issue_list, "new")
        assert len(self.api.repo.issues) == 2

        issue_list[0].title = "New Testing Issue"

        # Check the number of issues increases and that the
        # new issue is correct.
        assert len(self.api.repo.issues) == 2
        self.github.upload_issues(issue_list, "new")
        assert len(self.api.repo.issues) == 3

        assert self.api.repo.issues[2].number == 3
        assert self.api.repo.issues[2].title == "New Testing Issue"
        assert self.api.repo.issues[2].body == "Line 1\r\nLine 2"

    def test_update_comments_body(self) -> None:
        issue_list: List[GitHubIssue] = [
            GitHubIssue(
                number=1,
                title="Test Issue",
                complete=False,
                labels=["backlog", "personal"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["Line 1", "Line 2"],
                        tags=[],
                        updated_at="2018-08-19 18:18",
                    )
                ],
                metadata=[],
            )
        ]

        # Check the service is checked before being used.
        self.github.repo_name = ""
        assert self.nvim.message_print_count == 0
        self.github.update_comments(issue_list, "edit")
        assert self.nvim.message_print_count == 1

        self.github.repo_name = "CrossR/nvim_diary_template"
        self.nvim.message_print_count = 0
        self.nvim.errors = []

        # Check the issue doesn't change when there is no edit applied.
        assert self.api.repo.issues[0].body == "This is the main issue body"
        self.github.update_comments(issue_list, "edit")
        assert self.api.repo.issues[0].body == "This is the main issue body"
        assert self.nvim.messages[-1] == "Updated 0 comments on GitHub. "

        # Check non matching comment edits are skipped.
        issue_list[0].all_comments[0].tags = ["edit"]
        self.nvim.message_print_count = 0
        self.nvim.messages = []

        assert len(self.nvim.messages) == 0
        self.github.update_comments(issue_list, "edit")
        assert len(self.nvim.messages) == 2

        # Sort the updated time and then actually test a valid edit is applied.
        issue_list[0].all_comments[0].updated_at = "2018-01-01 10:00"
        issue_list[0].all_comments[0].body = ["Line 1", "Line 2", "Line 3"]

        self.github.update_comments(issue_list, "edit")
        assert self.api.repo.issues[0].body == "Line 1\r\nLine 2\r\nLine 3"

    def test_update_comment_normal(self) -> None:
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
                        updated_at="2018-08-19 18:18",
                    ),
                    GitHubIssueComment(
                        number=2,
                        body=["After the edit"],
                        tags=["edit"],
                        updated_at="2018-08-19 18:18",
                    ),
                ],
                metadata=[],
            )
        ]

        self.api.repo.issues[0].comments.append(
            MockGitHubComment(
                number=1,
                body="Before the edit",
                updated_at=parser.parse("2018-01-01 10:00"),
            )
        )

        # Check non matching comment edits are skipped.
        self.nvim.message_print_count = 0
        self.nvim.messages = []

        assert len(self.nvim.messages) == 0
        self.github.update_comments(issue_list, "edit")
        assert len(self.nvim.messages) == 2

        # Sort the updated time and then actually test a valid edit is applied.
        issue_list[0].all_comments[2].updated_at = "2018-01-01 10:00"

        self.github.update_comments(issue_list, "edit")
        assert self.api.repo.issues[0].comments[1].body == "After the edit"

    def test_update_issues(self) -> None:
        issue_list: List[GitHubIssue] = [
            GitHubIssue(
                number=1,
                title="Test Issue",
                complete=False,
                labels=["backlog", "personal"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["Line 1", "Line 2"],
                        tags=[],
                        updated_at="2018-08-19 18:18",
                    )
                ],
                metadata=[],
            )
        ]

        # Check the service is checked before being used.
        self.github.repo_name = ""
        assert self.nvim.message_print_count == 0
        self.github.update_issues(issue_list, "edit")
        assert self.nvim.message_print_count == 1

        self.github.repo_name = "CrossR/nvim_diary_template"
        self.nvim.message_print_count = 0
        self.nvim.errors = []

        # Check that issue update doesn't change the issue when not needed.
        assert self.api.repo.issues[0].body == "This is the main issue body"
        self.github.update_issues(issue_list, "edit")
        assert self.api.repo.issues[0].body == "This is the main issue body"

        # Check the non-matching issues are ignored.
        issue_list[0].metadata = ["edit"]
        issue_list[0].all_comments[0].updated_at = "2019-01-01 10:00"
        self.nvim.message_print_count = 0
        self.nvim.messages = []

        assert len(self.nvim.messages) == 0
        self.github.update_issues(issue_list, "edit")
        assert len(self.nvim.messages) == 2

        issue_list[0].all_comments[0].updated_at = "2018-01-01 10:00"

        # Check a valid edit is applied correctly
        issue_list[0].title = "New Title"
        issue_list[0].labels = ["backlog", "personal", "blocked"]

        self.github.update_issues(issue_list, "edit")

        assert self.api.repo.issues[0].title == "New Title"
        newLabels: List[Any] = [label.name for label in self.api.repo.issues[0].labels]
        assert newLabels == ["backlog", "personal", "blocked"]

    def test_complete_issues(self) -> None:
        issue_list: List[GitHubIssue] = [
            GitHubIssue(
                number=1,
                title="Test Issue",
                complete=True,
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
                        updated_at="2018-08-19 18:18",
                    ),
                ],
                metadata=[],
            )
        ]

        # Check the service is checked before being used.
        self.github.repo_name = ""
        assert self.nvim.message_print_count == 0
        self.github.complete_issues(issue_list)
        assert self.nvim.message_print_count == 1

        self.github.repo_name = "CrossR/nvim_diary_template"
        self.nvim.message_print_count = 0
        self.nvim.errors = []

        # Check the state toggles correctly
        assert self.api.repo.issues[0].state == "open"
        self.github.complete_issues(issue_list)
        assert self.api.repo.issues[0].state == "closed"

        issue_list[0].complete = False
        assert self.api.repo.issues[0].state == "closed"
        self.github.complete_issues(issue_list)
        assert self.api.repo.issues[0].state == "open"

        # Check doesn't change if already correct.
        assert self.api.repo.issues[0].state == "open"
        self.github.complete_issues(issue_list)
        assert self.api.repo.issues[0].state == "open"

    def test_missing_service(self) -> None:

        # Setup an object with no service to check that.
        test_github: SimpleNvimGithub = SimpleNvimGithub(self.nvim, self.options, None)
        assert test_github.service_not_valid() == True

        self.nvim.message_print_count = 0
        self.nvim.errors = []

        assert test_github.get_repo_labels() == []
        assert test_github.get_associated_repos() == []
        assert test_github.get_all_open_issues() == []

        # Test uploads now.
        assert test_github.upload_comments([], "new") == ([], [])
        assert test_github.upload_issues([], "new") == ([], [])
        assert test_github.update_issues([], "edit") == ([], [])
        assert test_github.update_comments([], "edit") == ([], [])
        test_github.complete_issues([])

        # There should have been 8 messages, all the same.
        # Converting the list should result in 1 item, due to the
        # fact there is only one unique item.
        assert self.nvim.message_print_count == 8
        assert len(set(self.nvim.errors)) == 1

    def test_service_not_valid(self) -> None:
        assert self.github.active == True
        self.github.service = None
        assert self.github.active == False
