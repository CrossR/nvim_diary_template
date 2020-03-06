import unittest
from typing import Any, Dict, List, Union

from datetime import date
from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent
from ..classes.nvim_google_cal_class import SimpleNvimGoogleCal
from ..classes.plugin_options import PluginOptions
from ..utils.constants import ISO_FORMAT
from .mocks.mock_gcal import MockGCalService, get_mock_gcal
from .mocks.mock_nvim import MockNvim


class SimpleNvimGoogleCalTest(unittest.TestCase):
    """
    Tests for methods in the SimpleNvimGoogleCal class.
    """

    def setUp(self) -> None:
        self.nvim: MockNvim = MockNvim()
        api_setup = get_mock_gcal()

        self.api: MockGCalService = api_setup[0]
        self.options: PluginOptions = api_setup[1]

        self.google: SimpleNvimGoogleCal = SimpleNvimGoogleCal(
            self.nvim, self.options, self.api
        )

    def test_get_all_open_events(self) -> None:
        event_list: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 1",
                start="2019-11-10T12:00:00Z",
                end="2019-11-10T13:00:00Z",
            ),
            CalendarEvent(
                name="Event 2",
                start="2019-11-10T17:30:00Z",
                end="2019-11-10T18:30:00Z",
            ),
        ]

        diary_date: date = date(2019, 11, 10)
        result: List[CalendarEvent] = self.google.get_events_for_date(diary_date)
        assert result == event_list

    def test_service_is_not_ready(self) -> None:
        assert self.google.active == True
        self.google.service = None
        assert self.google.active == False

    def test_get_all_calendars(self) -> None:
        all_calendars: Dict[str, str] = {
            "NVim Notes": "NvimNotesCal123",
            "University Calendar": "UniCal123",
            "GMail Events": "gmail_events",
            "Personal Cal": "personal",
            "Contacts": "contactCal",
            "Holidays in United Kingdom": "holInUk",
        }

        result: Union[List[str], Dict[str, str]] = self.google.get_all_calendars()
        assert result == all_calendars

    def test_filter_calendars(self) -> None:
        filtered_calendars: Dict[str, str] = {
            "NVim Notes": "NvimNotesCal123",
            "University Calendar": "UniCal123",
            "GMail Events": "gmail_events",
            "Personal Cal": "personal",
        }

        self.google.options.calendar_filter_list = [
            "Contacts",
            "Holidays in United Kingdom",
        ]

        result: Dict[str, str] = self.google.filter_calendars()
        assert result == filtered_calendars

    def test_upload_to_calendar(self) -> None:
        all_events: List[CalendarEvent] = [
            CalendarEvent(
                name="Event 1",
                start=parser.parse("2019-11-10T12:00:00Z").strftime(ISO_FORMAT),
                end=parser.parse("2019-11-10T13:00:00Z").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 2",
                start=parser.parse("2019-11-10T17:30:00Z").strftime(ISO_FORMAT),
                end=parser.parse("2019-11-10T18:30:00Z").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 3",
                start=parser.parse("2019-11-10T18:30:00Z").strftime(ISO_FORMAT),
                end=parser.parse("2019-11-10T19:30:00Z").strftime(ISO_FORMAT),
            ),
            CalendarEvent(
                name="Event 4",
                start=parser.parse("2019-11-10T20:30:00Z").strftime(ISO_FORMAT),
                end=parser.parse("2019-11-10T22:30:00Z").strftime(ISO_FORMAT),
            ),
        ]

        self.google.events = [
            CalendarEvent(
                name="Event 3",
                start=parser.parse("2019-11-10T18:30:00Z").strftime(ISO_FORMAT),
                end=parser.parse("2019-11-10T19:30:00Z").strftime(ISO_FORMAT),
            ),
        ]

        self.google.upload_to_calendar(all_events, date.today())
        # 3 inserts + 6 calendar event look ups.
        assert self.google.service._events_call_num == 9

    def test_get_calendar_id(self) -> None:
        assert self.google.get_calendar_id() == "NvimNotesCal123"
        assert self.google.get_calendar_id("primary") == "primary"

        for cal_name, cal_id in self.google.all_calendars.items():
            assert self.google.get_calendar_id(cal_name) == cal_id
