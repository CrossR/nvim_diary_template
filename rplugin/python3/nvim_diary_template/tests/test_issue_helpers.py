
import unittest
from copy import deepcopy
from typing import List

from ..helpers.issue_helpers import (
    check_markdown_style,
    insert_edit_tag,
    insert_new_comment,
    insert_new_issue,
    toggle_issue_completion,
)
from .mocks.nvim import MockNvim


class issue_helpersTest(unittest.TestCase):
    """
    Tests for functions in the issue_helpers module.
    """

    def setUp(self) -> None:
        self.nvim: MockNvim = MockNvim()
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
            "### [ ] Issue {1}: +label:work",
            "",
            "#### Title: Test Issue 1",
            "",
            "#### Comment {0} - 2018-01-01 12:00:",
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
            "### [ ] Issue {1}: +label:work",
            "",
            "#### Title: Test Issue 1",
            "",
            "#### Comment {0} - 2018-01-01 12:00:",
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
        final_buffer[10] = "### [ ] Issue {1}: +label:work +edit"
        insert_edit_tag(self.nvim, "issue")
        assert self.nvim.current.buffer.lines == final_buffer

        # Reset the buffer and insert for comment.
        final_buffer[10] = "### [ ] Issue {1}: +label:work"
        self.nvim.current.buffer.lines = deepcopy(final_buffer)
        final_buffer[14] = "#### Comment {0} - 2018-01-01 12:00: +edit"
        insert_edit_tag(self.nvim, "comment")
        assert self.nvim.current.buffer.lines == final_buffer

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
            "### [ ] Issue {1}: +label:work",
            "",
            "#### Title: Test Issue 1",
            "",
            "#### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "### [ ] Issue {00}: +new",
            "",
            "#### Title: ",
            "",
            "#### Comment {0} - 0000-00-00 00:00: +new",
            "",
            "## Schedule",
            "",
            "",
        ]

        # Check a new issue is added, and the cursor is moved correctly.
        insert_new_issue(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer
        assert self.nvim.current.window.cursor == (20, 11)

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
            "### [ ] Issue {1}: +label:work",
            "",
            "#### Title: Test Issue 1",
            "",
            "#### Comment {0} - 2018-01-01 12:00:",
            "Test comment body.",
            "",
            "#### Comment {1} - 0000-00-00 00:00: +new",
            "",
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
            "### [ ] Issue {1}: +label:work",
            "",
            "#### Title: Test Issue 1",
            "",
            "#### Comment {0} - 2018-01-01 12:00:",
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
        final_buffer[10] = "### [X] Issue {1}: +label:work"
        toggle_issue_completion(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer

        # Toggle back
        final_buffer[10] = "### [ ] Issue {1}: +label:work"
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

    def test_sort_issues(self) -> None:
        raise NotImplementedError()  # TODO: test sort_issues

    def test_get_github_objects(self) -> None:
        raise NotImplementedError()  # TODO: test get_github_objects

    def test_split_comment(self) -> None:
        raise NotImplementedError()  # TODO: test split_comment

    def test_get_issue_index(self) -> None:
        raise NotImplementedError()  # TODO: test get_issue_index
