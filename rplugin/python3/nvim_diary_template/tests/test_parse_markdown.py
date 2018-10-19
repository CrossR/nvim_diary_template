import unittest
from copy import deepcopy
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
from .mocks.mock_nvim import MockNvim


class parse_markdownTest(unittest.TestCase):
    """
    Tests for functions in the parse_markdown module.
    """

    def setUp(self) -> None:
        self.nvim: MockNvim = MockNvim()
        self.nvim.current.buffer.name = "2018-01-01.md"
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
                start=parser.parse("2018-01-01 10:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 11:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 2",
                start=parser.parse("2018-01-01 19:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 22:00").strftime(ISO_FORMAT),
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
        issue_2.title = "Markdown Only Issue"

        issue_3 = deepcopy(default_issue)
        issue_3.number = 3
        issue_3.title = "API Only Issue"

        issue_4 = deepcopy(default_issue)
        issue_4.number = 4
        issue_4.title = "Issue with new markdown comment"

        issue_5 = deepcopy(default_issue)
        issue_5.number = 5
        issue_5.title = "Issue with editted markdown comment"

        issue_6 = deepcopy(default_issue)
        issue_6.number = 6
        issue_6.title = "Issue with editted in both"
        issue_6.all_comments[0].body = ["Edit 2."]
        issue_6.all_comments[0].updated_at = "2018-01-01 14:00"

        # Deep copy is needed here to stop changes being applied to both instances.
        api_issues: List[GitHubIssue] = [
            default_issue,
            issue_3,
            deepcopy(issue_4),
            deepcopy(issue_5),
            deepcopy(issue_6),
        ]

        # Add a new comment.
        issue_4.all_comments.append(
            GitHubIssueComment(
                number=1,
                body=["Test comment list:", "", " * Line 1", " * Line 2", " * Line 3"],
                tags=["new"],
                updated_at="0000-00-00 00:00",
            )
        )

        # Add an edit.
        issue_5.all_comments[0].body = ["Edit."]
        issue_5.all_comments[0].tags = ["edit"]
        issue_5.all_comments[0].updated_at = "2018-01-01 12:00"

        # Add a conflicting edit.
        issue_6.all_comments[0].body = ["Conflict."]
        issue_6.all_comments[0].tags = ["edit"]
        issue_6.all_comments[0].updated_at = "2018-01-01 12:00"

        # Deep copy is needed here to stop changes being applied to both instances.
        markdown_issues: List[GitHubIssue] = [
            default_issue,
            deepcopy(issue_2),
            deepcopy(issue_4),
            deepcopy(issue_5),
            deepcopy(issue_6),
        ]

        # Add the conflict comment to check it is added.
        # Also set the comment back to how it was at the start.
        issue_6.all_comments.append(
            GitHubIssueComment(
                number=1,
                body=["Conflict."],
                tags=["edit", "conflict"],
                updated_at="2018-01-01 12:00",
            )
        )
        issue_6.all_comments[0].body = ["Edit 2."]
        issue_6.all_comments[0].updated_at = "2018-01-01 14:00"
        issue_6.all_comments[0].tags = []

        final_issues: List[GitHubIssue] = [
            default_issue,
            issue_3,
            issue_4,
            issue_5,
            issue_6,
            issue_2,
        ]

        result: List[GitHubIssue] = combine_issues(
            self.nvim, markdown_issues, api_issues
        )
        assert result == final_issues
