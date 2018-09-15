
import unittest
from typing import Any

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..classes.github_issue_class import GitHubIssue
from ..utils.constants import ISO_FORMAT
from ..utils.make_markdown_file import generate_markdown_metadata, make_todays_diary
from .mocks.gcal import MockGCalService
from .mocks.github import MockGitHubService
from .mocks.nvim import MockNvim
from .mocks.options import MockPluginOptions


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
        # Check doesn't save over modified.
        nvim = MockNvim()
        make_todays_diary(nvim, options, gcal, github)
        assert len(nvim.current.buffer.lines) == 15
        assert nvim.commands == [":w"]

    def test_generate_markdown_metadata(self) -> None:
        raise NotImplementedError()  # TODO: test generate_markdown_metadata
