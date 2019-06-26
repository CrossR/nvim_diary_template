import unittest
from copy import deepcopy
from typing import Any, Dict, List

import pytest

from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..classes.plugin_options import PluginOptions
from ..helpers.issue_helpers import (
    check_markdown_style,
    get_github_objects,
    get_latest_update,
    insert_edit_tag,
    insert_new_comment,
    insert_new_issue,
    sort_issues,
    split_comment,
    toggle_issue_completion,
)
from .mocks.mock_nvim import MockNvim


class issue_helpersTest(unittest.TestCase):
    """
    Tests for functions in the issue_helpers module.
    """

    def setUp(self) -> None:
        self.nvim: MockNvim = MockNvim()
        self.options: PluginOptions = PluginOptions()
        self.nvim.current.buffer.lines = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

    def test_insert_edit_tag(self) -> None:
        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

        # No changes should be made at first, due to the cursor
        # position.
        insert_edit_tag(self.nvim, "issue")
        assert self.nvim.current.buffer.lines == final_buffer
        insert_edit_tag(self.nvim, "comment")
        assert self.nvim.current.buffer.lines == final_buffer

        # Move the cursor and then insert for an issue.
        self.nvim.current.window.cursor = (17, 0)
        final_buffer[10] = "#### [ ] Issue {1}: +label:work +edit"
        insert_edit_tag(self.nvim, "issue")
        assert self.nvim.current.buffer.lines == final_buffer

        # Reset the buffer and insert for comment.
        final_buffer[10] = "#### [ ] Issue {1}: +label:work"
        self.nvim.current.buffer.lines = deepcopy(final_buffer)
        final_buffer[14] = "##### Comment {0} - 2018-01-01 12:00: +edit"
        insert_edit_tag(self.nvim, "comment")
        assert self.nvim.current.buffer.lines == final_buffer

        # Check there is no error if there is no issues.
        # Test with both, neither should change the buffer.
        final_buffer[10:17] = []
        self.nvim.current.buffer.lines = deepcopy(final_buffer)
        self.nvim.current.window.cursor = (10, 0)

        insert_edit_tag(self.nvim, "comment")
        assert self.nvim.current.buffer.lines == final_buffer
        insert_edit_tag(self.nvim, "issue")
        assert self.nvim.current.buffer.lines == final_buffer

        # Check the errors are correctly raised.
        with pytest.raises(ValueError):
            insert_edit_tag(self.nvim, "fake-type")

    def test_insert_new_issue(self) -> None:
        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### [ ] Issue {00}: +new",
            "",
            "##### Title: ",
            "",
            "##### Comment {0} - 0000-00-00 00:00: +new",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Check a new issue is added, and the cursor is moved correctly.
        insert_new_issue(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer
        assert self.nvim.current.window.cursor == (27, 12)

    def test_insert_new_comment(self) -> None:
        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "##### Comment {1} - 0000-00-00 00:00: +new",
            "",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Check the buffer doesn't change at first, since we aren't in an issue.
        initial_buffer: List[str] = self.nvim.current.buffer.lines
        insert_new_comment(self.nvim)
        assert self.nvim.current.buffer.lines == initial_buffer
        assert self.nvim.current.window.cursor == (0, 0)

        # Now put the cursor in an issue, and check a new comment is added, and
        # the cursor is moved correctly.
        self.nvim.current.window.cursor = (13, 0)
        insert_new_comment(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer
        assert self.nvim.current.window.cursor == (19, 0)

    def test_insert_new_issue_in_group(self) -> None:
        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "### Work",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "### Personal",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### [ ] Issue {00}: +new",
            "",
            "##### Title: ",
            "",
            "##### Comment {0} - 0000-00-00 00:00: +new",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Set the buffer to contain groups.
        self.options.issue_groups = ["work", "personal"]
        self.nvim.current.buffer.lines = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "### Work",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "### Personal",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Check a new issue is added, and the cursor is moved correctly.
        insert_new_issue(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer
        assert self.nvim.current.window.cursor == (31, 12)

    def test_insert_new_group_comment(self) -> None:
        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "### Work",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "##### Comment {1} - 0000-00-00 00:00: +new",
            "",
            "### Personal",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Set the buffer to contain groups.
        self.options.issue_groups = ["work", "personal"]
        self.nvim.current.buffer.lines = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "### Work",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "### Personal",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Check the buffer doesn't change at first, since we aren't in an issue.
        initial_buffer: List[str] = self.nvim.current.buffer.lines
        insert_new_comment(self.nvim)
        assert self.nvim.current.buffer.lines == initial_buffer
        assert self.nvim.current.window.cursor == (0, 0)

        # Now put the cursor in an issue, and check a new comment is added, and
        # the cursor is moved correctly.
        self.nvim.current.window.cursor = (13, 0)
        insert_new_comment(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer
        assert self.nvim.current.window.cursor == (19, 0)

    def test_toggle_issue_completion(self) -> None:
        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "#### [ ] Issue {1}: +label:work",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### [ ] Issue {2}: +label:personal",
            "",
            "##### Title: Test Issue 1",
            "",
            "##### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "## Schedule",
            "",
            "",
        ]

        # No changes should be made at first, due to the cursor
        # position.
        toggle_issue_completion(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer

        # Move the cursor and then complete the issue.
        self.nvim.current.window.cursor = (17, 0)
        final_buffer[10] = "#### [X] Issue {1}: +label:work"
        toggle_issue_completion(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer

        # Toggle back
        final_buffer[10] = "#### [ ] Issue {1}: +label:work"
        toggle_issue_completion(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer

    def test_check_markdown_style(self) -> None:
        vimwiki: str = " - [X] Test ToDo"
        vimwiki_1: str = " - [o] Test ToDo"
        github: str = " - [x] Test ToDo"
        empty: str = " - [ ] Test ToDo"

        # Check they aren't changed when correct.
        result: str = check_markdown_style(github, "github")
        assert result == github

        result = check_markdown_style(vimwiki, "vimwiki")
        assert result == vimwiki

        result = check_markdown_style(vimwiki_1, "vimwiki")
        assert result == vimwiki_1

        # Empty is valid in either
        result = check_markdown_style(empty, "vimwiki")
        assert result == empty

        result = check_markdown_style(empty, "github")
        assert result == empty

        # Are vimwiki states swapped?
        result = check_markdown_style(vimwiki_1, "github")
        assert result == empty
        result = check_markdown_style(vimwiki, "github")
        assert result == github

        # Are GitHub states swapped?
        result = check_markdown_style(github, "vimwiki")
        assert result == vimwiki

        # Check other tests raise an exception.
        with pytest.raises(Exception):
            check_markdown_style(github, "fake-type")

    def test_sort_issues(self) -> None:
        default_issue: GitHubIssue = GitHubIssue(
            number=1,
            title="Test Issue 1",
            complete=False,
            labels=["work"],
            metadata=[],
            all_comments=[
                GitHubIssueComment(
                    number=0,
                    body=["Test comment body."],
                    tags=[],
                    updated_at="2018-01-01 12:00",
                )
            ],
        )

        issue_2 = deepcopy(default_issue)
        issue_2.number = 2
        issue_2.title = "Complete"
        issue_2.complete = True

        issue_3 = deepcopy(default_issue)
        issue_3.number = 3
        issue_3.title = "Blocked"
        issue_3.labels = ["blocked"]

        issue_4 = deepcopy(default_issue)
        issue_4.number = 4
        issue_4.title = "2) In Progress"
        issue_4.labels = ["inprogress"]

        issue_5 = deepcopy(default_issue)
        issue_5.number = 5
        issue_5.title = "Backlog"
        issue_5.labels = ["backlog"]

        issue_6 = deepcopy(default_issue)
        issue_6.number = 6
        issue_6.title = "3) In Progress"
        issue_6.labels = ["inprogress"]

        # First, due to being in progress and latest edit.
        issue_7 = deepcopy(default_issue)
        issue_7.number = 7
        issue_7.title = "1) In Progress"
        issue_7.labels = ["inprogress"]
        issue_7.all_comments[0].updated_at = "2018-01-01 22:00"

        unsorted_list: List[GitHubIssue] = [
            deepcopy(default_issue),
            deepcopy(issue_2),
            deepcopy(issue_3),
            deepcopy(issue_4),
            deepcopy(issue_5),
            deepcopy(issue_6),
            deepcopy(issue_7),
        ]

        sorted_list: List[GitHubIssue] = [
            deepcopy(issue_7),
            deepcopy(issue_4),
            deepcopy(issue_6),
            deepcopy(default_issue),
            deepcopy(issue_3),
            deepcopy(issue_5),
            deepcopy(issue_2),
        ]

        result: List[GitHubIssue] = sort_issues(self.options, unsorted_list)
        assert result == sorted_list

    def test_get_github_objects(self) -> None:
        dicts_to_check: List[Dict[str, Any]] = [
            {
                "number": 1,
                "title": "Test Issue",
                "complete": False,
                "labels": ["backlog", "personal"],
                "all_comments": [
                    {
                        "number": 0,
                        "body": ["Line 1", "Line 2"],
                        "tags": [],
                        "updated_at": "2018-08-19 18:18",
                    }
                ],
                "metadata": [],
            },
            {
                "number": 2,
                "title": "Test Issue 2",
                "complete": False,
                "labels": ["inprogress", "work"],
                "all_comments": [
                    {
                        "number": 0,
                        "body": ["Line 1", "Line 2"],
                        "tags": [],
                        "updated_at": "2018-08-19 18:18",
                    },
                    {
                        "number": 1,
                        "body": ["Line 2-1", "Line 2-2"],
                        "tags": [],
                        "updated_at": "2018-08-19 12:18",
                    },
                ],
                "metadata": [],
            },
        ]

        converted_dicts: List[GitHubIssue] = [
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
            ),
            GitHubIssue(
                number=2,
                title="Test Issue 2",
                complete=False,
                labels=["inprogress", "work"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["Line 1", "Line 2"],
                        tags=[],
                        updated_at="2018-08-19 18:18",
                    ),
                    GitHubIssueComment(
                        number=1,
                        body=["Line 2-1", "Line 2-2"],
                        tags=[],
                        updated_at="2018-08-19 12:18",
                    ),
                ],
                metadata=[],
            ),
        ]

        # Check dicts are converted.
        result: Any = get_github_objects(dicts_to_check)
        assert result == converted_dicts

        # Check objects are left alone.
        result = get_github_objects(converted_dicts)
        assert result == converted_dicts

    def test_get_latest_update(self) -> None:
        inital_issue: GitHubIssue = GitHubIssue(
            number=1,
            title="Test Issue 1",
            complete=False,
            labels=["inprogress", "work"],
            all_comments=[
                GitHubIssueComment(
                    number=0,
                    body=["Line 1", "Line 2"],
                    tags=[],
                    updated_at="2018-08-19 18:18",
                ),
                GitHubIssueComment(
                    number=1,
                    body=["Line 2-1", "Line 2-2"],
                    tags=[],
                    updated_at="2018-12-19 12:18",
                ),
                GitHubIssueComment(
                    number=1,
                    body=["Line 3-1", "Line 3-2"],
                    tags=[],
                    updated_at="2018-08-19 12:18",
                ),
            ],
            metadata=[],
        )
        expected_date: str = "2018-12-19 12:18"

        result: str = get_latest_update(inital_issue.all_comments)
        assert result == expected_date

    def test_split_comment(self) -> None:
        initial_comment: str = "\nThis is comments line 1.\nAnd this is line 2.\nAnd the line 3!\n\n"
        final_comment: List[str] = [
            "This is comments line 1.",
            "And this is line 2.",
            "And the line 3!",
        ]

        result: List[str] = split_comment(initial_comment)
        assert result == final_comment
