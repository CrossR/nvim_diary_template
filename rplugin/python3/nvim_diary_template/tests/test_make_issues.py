
import unittest
from copy import deepcopy
from typing import Dict, List

from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..utils.make_issues import (
    produce_issue_markdown,
    remove_tag_from_issues,
    set_issues_from_issues_list,
)
from .mocks.nvim import MockNvim


class make_issuesTest(unittest.TestCase):
    """
    Tests for functions in the make_issues module.
    """

    def setUp(self) -> None:
        self.nvim = MockNvim()
        self.set_buffer()

        self.issues: List[GitHubIssue] = [
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
                complete=True,
                labels=["personal"],
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
                number=3,
                title="Test Issue 3",
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
                        tags=["edit"],
                        updated_at="2018-08-19 12:18",
                    ),
                ],
                metadata=[],
            ),
        ]

    def set_buffer(self):
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
            "## Schedule",
            "",
        ]

    def test_produce_issue_markdown(self) -> None:
        # This should be sorted, which is why 2 is first.
        final_buffer: List[str] = [
            "## Issues",
            "",
            "### [ ] Issue {3}: +label:inprogress +label:work",
            "",
            "#### Title: Test Issue 3",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "#### Comment {1} - 2018-08-19 12:18: +edit",
            "Line 2-1",
            "Line 2-2",
            "",
            "### [ ] Issue {1}: +label:backlog +label:personal",
            "",
            "#### Title: Test Issue",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "### [X] Issue {2}: +label:personal",
            "",
            "#### Title: Test Issue 2",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
        ]

        result: List[str] = produce_issue_markdown(self.issues)
        assert result == final_buffer

    def test_remove_tag_from_issues(self) -> None:
        # Basic test to remove an edit tag.
        result: List[GitHubIssue] = remove_tag_from_issues(
            deepcopy(self.issues), "edit"
        )
        assert len(result) == 3
        assert result[2].all_comments[1].tags == []

        # Check only tags in that scope are removed.
        result = remove_tag_from_issues(deepcopy(self.issues), "edit", "issues")
        assert result[2].all_comments[1].tags == ["edit"]

        # Check only tags in that scope are removed.
        result = remove_tag_from_issues(deepcopy(self.issues), "edit", "comments")
        assert result[2].all_comments[1].tags == []

        # Check ignored tags are left.
        ignore_list: List[Dict[str, int]] = [{"issue": 2, "comment": 1}]
        result = remove_tag_from_issues(
            deepcopy(self.issues), "edit", "comments", ignore_list
        )
        assert result[2].all_comments[1].tags == ["edit"]

    def test_set_issues_from_issues_list(self) -> None:
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
            "### [ ] Issue {3}: +label:inprogress +label:work",
            "",
            "#### Title: Test Issue 3",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "#### Comment {1} - 2018-08-19 12:18: +edit",
            "Line 2-1",
            "Line 2-2",
            "",
            "### [ ] Issue {1}: +label:backlog +label:personal",
            "",
            "#### Title: Test Issue",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "### [X] Issue {2}: +label:personal",
            "",
            "#### Title: Test Issue 2",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "## Schedule",
            "",
        ]

        # Check buffer is properly set.
        set_issues_from_issues_list(self.nvim, self.issues, True)
        assert self.nvim.current.buffer.lines == final_buffer

        final_buffer = [
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
            "### [ ] Issue {1}: +label:backlog +label:personal",
            "",
            "#### Title: Test Issue",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "### [X] Issue {2}: +label:personal",
            "",
            "#### Title: Test Issue 2",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "### [ ] Issue {3}: +label:inprogress +label:work",
            "",
            "#### Title: Test Issue 3",
            "",
            "#### Comment {0} - 2018-08-19 18:18:",
            "Line 1",
            "Line 2",
            "",
            "#### Comment {1} - 2018-08-19 12:18: +edit",
            "Line 2-1",
            "Line 2-2",
            "",
            "## Schedule",
            "",
        ]

        # Check sorting works.
        self.set_buffer()
        set_issues_from_issues_list(self.nvim, self.issues, False)
        assert self.nvim.current.buffer.lines == final_buffer
