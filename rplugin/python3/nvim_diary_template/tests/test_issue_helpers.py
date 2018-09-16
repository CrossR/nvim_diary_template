
import unittest
from unittest.mock import MagicMock, create_autospec

from .mocks.nvim import MockNvim
from ..helpers.issue_helpers import insert_edit_tag, insert_new_issue, insert_new_comment
from typing import List

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
        raise NotImplementedError()

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
        raise NotImplementedError()  # TODO: test toggle_issue_completion

    def test_check_markdown_style(self) -> None:
        raise NotImplementedError()  # TODO: test check_markdown_style

    def test_convert_utc_timezone(self) -> None:
        raise NotImplementedError()  # TODO: test convert_utc_timezone

    def test_sort_issues(self) -> None:
        raise NotImplementedError()  # TODO: test sort_issues

    def test_sort_completion_state(self) -> None:
        raise NotImplementedError()  # TODO: test sort_completion_state

    def test_get_github_objects(self) -> None:
        raise NotImplementedError()  # TODO: test get_github_objects

    def test_split_comment(self) -> None:
        raise NotImplementedError()  # TODO: test split_comment

    def test_get_issue_index(self) -> None:
        raise NotImplementedError()  # TODO: test get_issue_index
