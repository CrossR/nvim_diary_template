
import unittest
from typing import List
from .mocks.nvim import MockNvim
from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..classes.calendar_event_class import CalendarEvent
from ..utils.parse_markdown import (
    remove_events_not_from_today,
    parse_markdown_file_for_issues,
    parse_markdown_file_for_events,
)
from ..utils.constants import ISO_FORMAT
from dateutil import parser


class parse_markdownTest(unittest.TestCase):
    """
    Tests for functions in the parse_markdown module.
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
            "#### Comment {1} - 0000-00-00 00:00: +new",
            "Test comment list:",
            "",
            " * Line 1",
            " * Line 2",
            " * Line 3",
            "",
            "### [ ] Issue {00}: +new",
            "",
            "#### Title: New Issue 2",
            "",
            "#### Comment {0} - 0000-00-00 00:00: +new",
            "New issue body.",
            "",
            "## Schedule",
            "",
            "- 10:00 - 11:00: Event 1",
            "- 19:00 - 22:00: Event 2",
            "",
        ]

    def test_remove_events_not_from_today(self) -> None:
        raise NotImplementedError()  # TODO: test remove_events_not_from_today

    def test_parse_markdown_file_for_events(self) -> None:
        events: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 1",
                start=parser.parse("10:00").strftime(ISO_FORMAT),
                end=parser.parse("11:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 2",
                start=parser.parse("19:00").strftime(ISO_FORMAT),
                end=parser.parse("22:00").strftime(ISO_FORMAT),
            ),
        ]

        result: List[CalendarEvent] = parse_markdown_file_for_events(
            self.nvim, ISO_FORMAT
        )
        assert result == events

    def test_parse_markdown_file_for_issues(self) -> None:
        issues: List[GitHubIssue] = [
            GitHubIssue(
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
                    ),
                    GitHubIssueComment(
                        number=1,
                        body=[
                            "Test comment list:",
                            "",
                            " * Line 1",
                            " * Line 2",
                            " * Line 3",
                        ],
                        tags=["new"],
                        updated_at="0000-00-00 00:00",
                    ),
                ],
            ),
            GitHubIssue(
                number=0,
                title="New Issue 2",
                complete=False,
                labels=[],
                metadata=["new"],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["New issue body."],
                        tags=["new"],
                        updated_at="0000-00-00 00:00",
                    )
                ],
            ),
        ]

        result: List[GitHubIssue] = parse_markdown_file_for_issues(self.nvim)
        assert result == issues

    def test_combine_events(self) -> None:
        raise NotImplementedError()  # TODO: test combine_events

    def test_combine_issues(self) -> None:
        raise NotImplementedError()  # TODO: test combine_issues
