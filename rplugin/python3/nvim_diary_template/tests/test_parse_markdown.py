
import unittest
from typing import List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..utils.constants import ISO_FORMAT
from ..utils.parse_markdown import (
    combine_events,
    combine_issues,
    parse_markdown_file_for_events,
    parse_markdown_file_for_issues,
    remove_events_not_from_today,
)
from .mocks.nvim import MockNvim


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
            "- 25/01/2018 12:00 - 25/01/2018 13:00: Meeting with Alex",
        ]

    def test_remove_events_not_from_today(self) -> None:
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
        ]

        remove_events_not_from_today(self.nvim)
        assert self.nvim.current.buffer.lines == final_buffer

    def test_parse_markdown_file_for_events(self) -> None:
        # Currently, we assume an event is today if no date is given.
        # If the diary date is ever used, should update this.
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
            CalendarEvent(
                name="Meeting with Alex",
                start=parser.parse("2018-01-25 12:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-25 13:00").strftime(ISO_FORMAT),
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
        markdown_events: List[CalendarEvent] = [
            CalendarEvent(name="Event 1", start="10:00", end="11:00"),
            CalendarEvent(name="Event 2", start="14:00", end="15:00"),
            CalendarEvent(name="Event 5", start="19:00", end="22:00"),
        ]

        api_events: List[CalendarEvent] = [
            CalendarEvent(name="Event 1", start="10:00", end="11:00"),
            CalendarEvent(name="Event 3", start="14:00", end="16:00"),
            CalendarEvent(name="Event 4", start="19:00", end="22:00"),
        ]

        final_list: List[CalendarEvent] = [
            CalendarEvent(name="Event 1", start="10:00", end="11:00"),
            CalendarEvent(name="Event 2", start="14:00", end="15:00"),
            CalendarEvent(name="Event 5", start="19:00", end="22:00"),
            CalendarEvent(name="Event 3", start="14:00", end="16:00"),
            CalendarEvent(name="Event 4", start="19:00", end="22:00"),
        ]

        # This has the following:
        # * Duplicated Events.
        # * API Only events.
        # * Calendar Only Events
        # Does not test or work for events that are not from today.
        # Events should not be sorted.
        result: List[CalendarEvent] = combine_events(markdown_events, api_events)
        assert result == final_list

    def test_combine_issues(self) -> None:
        raise NotImplementedError()  # TODO: test combine_issues
