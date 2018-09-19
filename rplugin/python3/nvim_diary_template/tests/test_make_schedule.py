
import unittest
from typing import List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..utils.constants import ISO_FORMAT, TIME_FORMAT
from ..utils.make_schedule import (
    format_events_lines,
    produce_schedule_markdown,
    set_schedule_from_events_list,
)
from .mocks.nvim import MockNvim


class make_scheduleTest(unittest.TestCase):
    """
    Tests for functions in the make_schedule module.
    """

    def setUp(self) -> None:
        self.nvim = MockNvim()
        self.set_buffer()

    def set_buffer(self) -> None:
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

    def test_produce_schedule_markdown(self) -> None:
        final_buffer: List[str] = [
            "## Schedule",
            "",
            "- 10:00 - 11:00: Event 1",
            "- 14:00 - 15:00: Event 2",
            "- 14:00 - 16:00: Event 3",
            "",
        ]

        events: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 1",
                start=parser.parse("2018-01-01 10:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 11:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 2",
                start=parser.parse("2018-01-01 14:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 15:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 3",
                start=parser.parse("2018-01-01 14:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 16:00").strftime(ISO_FORMAT),
            ),
        ]

        result: List[str] = produce_schedule_markdown(events)
        assert result == final_buffer

    def test_set_schedule_from_events_list(self) -> None:
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
            "## Schedule",
            "",
            "- 10:00 - 11:00: Event 1",
            "- 14:00 - 15:00: Event 2",
            "- 14:00 - 16:00: Event 3",
            "",
        ]

        events: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 1",
                start=parser.parse("2018-01-01 10:00").strftime(TIME_FORMAT),
                end=parser.parse("2018-01-01 11:00").strftime(TIME_FORMAT),
            ),
            CalendarEvent(
                name="Event 2",
                start=parser.parse("2018-01-01 14:00").strftime(TIME_FORMAT),
                end=parser.parse("2018-01-01 15:00").strftime(TIME_FORMAT),
            ),
            CalendarEvent(
                name="Event 3",
                start=parser.parse("2018-01-01 14:00").strftime(TIME_FORMAT),
                end=parser.parse("2018-01-01 16:00").strftime(TIME_FORMAT),
            ),
        ]

        set_schedule_from_events_list(self.nvim, events, True)
        assert self.nvim.current.buffer.lines == final_buffer
