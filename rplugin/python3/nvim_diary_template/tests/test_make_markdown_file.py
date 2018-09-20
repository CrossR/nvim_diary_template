
import unittest
from typing import Any, Dict, List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..utils.constants import ISO_FORMAT
from ..utils.make_markdown_file import generate_markdown_metadata, make_todays_diary
from .mocks.mock_gcal import MockGCalService
from .mocks.mock_github import get_mock_github
from .mocks.mock_nvim import MockNvim
from .mocks.mock_options import MockPluginOptions


class make_markdown_fileTest(unittest.TestCase):
    """
    Tests for functions in the make_markdown_file module.
    """

    def test_make_todays_diary(self) -> None:
        nvim: Any = MockNvim()
        gcal: Any = MockGCalService()
        github: Any = get_mock_github(nvim)
        options: Any = MockPluginOptions()

        # Check defaults work and is saved.
        # This includes Issues
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 41
        assert nvim.commands == [":w"]

        # Check doesn't save over modified.
        nvim = MockNvim()
        nvim.current.buffer.lines = ["Edited!"]
        make_todays_diary(nvim, options, gcal, github)
        assert nvim.current.buffer.lines == ["Edited!"]
        assert nvim.commands == []

        gcal.events.extend(
            [
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
            ]
        )

        # Check events are added.
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 43

        # But not when disabled.
        options.use_google_calendar = False
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 41
        options.use_google_calendar = True

        # Check issues are added.
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 43

        # But not when disabled.
        options.use_github_repo = False
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 15
        options.use_github_repo = True

        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        final_markdown: List[str] = [
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "### [ ] Issue {2}: +label:inprogress +label:work",
            "",
            "#### Title: Test Issue 2",
            "",
            "#### Comment {0} - 2018-01-01 10:00:",
            "This is the second issue body:",
            "    * Item 1",
            "    * Item 2",
            "",
            "#### Comment {1} - 2018-08-19 19:18:",
            "Line 1",
            "Line 2",
            "",
            "#### Comment {2} - 2018-08-19 13:18:",
            "Line 2-1",
            "Line 2-2",
            "",
            "### [ ] Issue {1}: +label:backlog +label:personal",
            "",
            "#### Title: Test Issue",
            "",
            "#### Comment {0} - 2018-01-01 10:00:",
            "This is the main issue body",
            "",
            "#### Comment {1} - 2018-08-19 19:18:",
            "Line 1",
            "Line 2",
            "",
            "## Schedule",
            "",
            "- 10:00 - 11:00: Event 1",
            "- 19:00 - 22:00: Event 2",
            "",
        ]

        assert final_markdown == nvim.current.buffer.lines[5:]

    def test_generate_markdown_metadata(self) -> None:

        diary_metadata: Dict[str, str] = {"Date": "2018-01-01"}
        result: List[str] = generate_markdown_metadata(diary_metadata)

        example: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
        ]
        assert result == example

        diary_metadata = {"Date": "2018-01-01", "Title": "Python Unit Tests"}
        result = generate_markdown_metadata(diary_metadata)

        example = [
            "<!---",
            "    Date: 2018-01-01",
            "    Title: Python Unit Tests",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
        ]
        assert result == example
