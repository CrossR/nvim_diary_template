
import unittest
from typing import List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..helpers.event_helpers import format_event, sort_events
from ..utils.constants import ISO_FORMAT


class event_helpersTest(unittest.TestCase):
    """
    Tests for functions in the event_helpers module.
    """

    def test_sort_events(self) -> None:
        # This test 3 things:
        #  Start Time
        #  End Time
        #  Matching both, so using the name.
        unsorted_events: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 2",
                start=parser.parse("2018-01-01 14:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 15:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 4",
                start=parser.parse("2018-01-01 19:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 22:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 3",
                start=parser.parse("2018-01-01 14:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 16:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 1",
                start=parser.parse("2018-01-01 10:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 11:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 5",
                start=parser.parse("2018-01-01 19:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 22:00").strftime(ISO_FORMAT),
            ),
        ]

        sorted_events: List[CalendarEvent] = [
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
            CalendarEvent(
                name="Event 4",
                start=parser.parse("2018-01-01 19:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 22:00").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 5",
                start=parser.parse("2018-01-01 19:00").strftime(ISO_FORMAT),
                end=parser.parse("2018-01-01 22:00").strftime(ISO_FORMAT),
            ),
        ]

        result: List[CalendarEvent] = sort_events(unsorted_events)

        assert result == sorted_events

    def test_format_event(self) -> None:
        formatted_event: CalendarEvent = CalendarEvent(
            name="Event 1",
            start=parser.parse("2018-01-01 14:00").strftime(ISO_FORMAT),
            end=parser.parse("2018-01-01 15:00").strftime(ISO_FORMAT),
        )

        unformatted_event: CalendarEvent = CalendarEvent(
            name="Event 1", start="2018-01-01 14:00", end="2018-01-01 15:00"
        )

        result: CalendarEvent = format_event(unformatted_event, ISO_FORMAT)

        assert result == formatted_event
