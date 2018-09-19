
import unittest
from typing import Any, Dict, List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..utils.constants import ISO_FORMAT
from ..utils.make_markdown_file import generate_markdown_metadata, make_todays_diary
from .mocks.mock_gcal import MockGCalService
from .mocks.mock_github import MockGitHubService
from .mocks.mock_nvim import MockNvim
from .mocks.mock_options import MockPluginOptions


class make_markdown_fileTest(unittest.TestCase):
    """
    Tests for functions in the make_markdown_file module.
    """

    def test_make_todays_diary(self) -> None:
        nvim: Any = MockNvim()
        gcal: Any = MockGCalService()
        github: Any = MockGitHubService()
        options: Any = MockPluginOptions()

        # Check defaults work and is saved.
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 13
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
        assert len(nvim.current.buffer.lines) == 15

        # But not when disabled.
        options.use_google_calendar = False
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 13
        options.use_google_calendar = True

        github.issues.append(
            GitHubIssue(
                number=1,
                title="Test Issue 1",
                complete=False,
                labels=[],
                metadata=[],
                all_comments=[
                    GitHubIssueComment(
                        number=0,
                        body=["Test comment body."],
                        tags=[],
                        updated_at=parser.parse("2018-01-01 12:00").strftime(
                            ISO_FORMAT
                        ),
                    )
                ],
            )
        )

        # Check issues are added.
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 22

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
            "### [ ] Issue {1}:",
            "",
            "#### Title: Test Issue 1",
            "",
            "#### Comment {0} - 2018-01-01T12:00:00.000000:",
            "Test comment body.",
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
