import unittest
from typing import Any, List

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

    def test_get_all_open_issues(self) -> None:
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

        result: List[CalendarEvent] = self.google.get_events_for_date(date.today())
        assert result == event_list
