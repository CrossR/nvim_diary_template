import unittest
from typing import Any, Dict, List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..helpers.google_calendar_helpers import (
    convert_events,
    create_google_event,
    format_google_events,
    get_calendar_objects,
)
from ..utils.constants import ISO_FORMAT


class google_calendar_helpersTest(unittest.TestCase):
    """
    Tests for functions in the google_calendar_helpers module.
    """

    def setUp(self) -> None:
        pass  # TODO

    def test_convert_events(self) -> None:
        before_conversion: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 1", start="2018-01-01 10:00", end="2018-01-01 11:00"
            ),
            CalendarEvent(
                name="Event 2", start="2018-01-01 14:00", end="2018-01-01 15:00"
            ),
            CalendarEvent(
                name="Event 3", start="2018-01-01 14:00", end="2018-01-01 16:00"
            ),
        ]
        after_conversion: List[CalendarEvent] = [
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

        result: List[CalendarEvent] = convert_events(before_conversion, ISO_FORMAT)
        assert result == after_conversion

    def test_format_google_events(self) -> None:
        # Test the following:
        # Parsing date.
        # Parsing datetime.
        # Parsing date and removing due to wrong day.
        # Parsing datetime and removing due to wrong day.
        before_conversion: List[Dict[str, Any]] = [
            {
                "summary": "Test Event 1",
                "start": {"dateTime": "2018-09-16T14:00:00+01:00"},
                "end": {"dateTime": "2018-09-16T15:00:00+01:00"},
            },
            {
                "summary": "Test Event 2",
                "start": {"date": "2018-09-16"},
                "end": {"date": "2018-09-17"},
            },
            {
                "summary": "Test Event 3",
                "start": {"dateTime": "2018-01-01T14:00:00+01:00"},
                "end": {"dateTime": "2018-01-01T15:00:00+01:00"},
            },
            {
                "summary": "Test Event 4",
                "start": {"date": "2018-01-01"},
                "end": {"date": "2018-01-02"},
            },
        ]
        after_conversion: List[CalendarEvent] = [
            CalendarEvent(
                name="Test Event 3",
                start="2018-01-01T14:00:00+01:00",
                end="2018-01-01T15:00:00+01:00",
            ),
            CalendarEvent(name="Test Event 4", start="2018-01-01", end="2018-01-02"),
        ]

        result: List[CalendarEvent] = format_google_events(
            before_conversion, "2018-01-01"
        )
        assert result == after_conversion

    def test_create_google_event(self) -> None:
        before_conversion: List[CalendarEvent] = [
            CalendarEvent(
                name="Test Event 1",
                start="2018-01-01T14:00:00+01:00",
                end="2018-01-01T15:00:00+01:00",
            ),
            CalendarEvent(name="Test Event 2", start="2018-01-01", end="2018-01-02"),
        ]

        after_conversion: List[Dict[str, Any]] = [
            {
                "summary": "Test Event 1",
                "start": {
                    "dateTime": "2018-01-01T14:00:00+01:00",
                    "timeZone": "Europe/London",
                },
                "end": {
                    "dateTime": "2018-01-01T15:00:00+01:00",
                    "timeZone": "Europe/London",
                },
            },
            {
                "summary": "Test Event 2",
                "start": {
                    "dateTime": "2018-01-01T00:00:00",
                    "timeZone": "Europe/London",
                },
                "end": {"dateTime": "2018-01-02T00:00:00", "timeZone": "Europe/London"},
            },
        ]

        # Check for a normal event.
        result: Dict[str, Any] = create_google_event(
            before_conversion[0], "Europe/London"
        )
        assert result == after_conversion[0]

        # Check for an all day event.
        result = create_google_event(before_conversion[1], "Europe/London")
        assert result == after_conversion[1]

    def test_get_calendar_objects(self) -> None:
        # Check that a dict is properly converted.
        dicts_to_check: List[Dict[str, Any]] = [
            {
                "name": "Test Event 1",
                "start": "2018-09-16T14:00:00+01:00",
                "end": "2018-09-16T15:00:00+01:00",
            },
            {"name": "Test Event 2", "start": "2018-09-16", "end": "2018-09-17"},
        ]
        converted_dicts: List[CalendarEvent] = [
            CalendarEvent(
                name="Test Event 1",
                start="2018-09-16T14:00:00+01:00",
                end="2018-09-16T15:00:00+01:00",
            ),
            CalendarEvent(name="Test Event 2", start="2018-09-16", end="2018-09-17"),
        ]

        # Check dicts are converted.
        result: Any = get_calendar_objects(dicts_to_check)
        assert result == converted_dicts

        # Check that objects are left alone.
        objects_to_check: List[CalendarEvent] = [
            CalendarEvent(
                name="Test Event 3",
                start="2018-01-01T14:00:00+01:00",
                end="2018-01-01T15:00:00+01:00",
            ),
            CalendarEvent(name="Test Event 4", start="2018-01-01", end="2018-01-02"),
        ]

        result = get_calendar_objects(objects_to_check)
        assert result == objects_to_check
