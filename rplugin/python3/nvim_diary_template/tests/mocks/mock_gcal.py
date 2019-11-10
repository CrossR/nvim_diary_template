from __future__ import annotations

from datetime import date
from typing import Any, List, Callable, Dict, Tuple
from tempfile import mkdtemp

from ...classes.calendar_event_class import CalendarEvent
from ...classes.plugin_options import PluginOptions


def get_mock_gcal() -> Tuple[MockGCalService, PluginOptions]:
    new_api: MockGCalService = MockGCalService()
    options: PluginOptions = PluginOptions()

    # Setup options
    options.config_path = mkdtemp()
    options.repo_name = "CrossR/nvim_diary_template"

    # Setup the GCal Mock API
    new_api._event_json = {
        "kind": "calendar#events",
        "summary": "GMail Events",
        "updated": "2019-11-10T19:25:00.179Z",
        "timeZone": "Europe/London",
        "items": [
            {
                "summary": "Event 1",
                "start": {"dateTime": "2019-11-10T12:00:00Z"},
                "end": {"dateTime": "2019-11-10T13:00:00Z"},
            },
            {
                "summary": "Event 2",
                "start": {"dateTime": "2019-11-10T17:30:00Z"},
                "end": {"dateTime": "2019-11-10T18:30:00Z"},
            },
        ],
    }

    new_api._cal_json = {
        "kind": "calendar#calendarList",
        "items": [
            {
                "id": "NvimNotesCal123",
                "summary": "NVim Notes",
            },
            {
                "id": "UniCal123",
                "summary": "University Calendar",
            },
            {
                "id": "gmail_events",
                "summary": "GMail Events",
            },
            {
                "id": "personal",
                "summary": "Personal Cal",
            },
            {
                "id": "contactCal",
                "summary": "Contacts",
            },
            {
                "id": "holInUk",
                "summary": "Holidays in United Kingdom",
            },
        ],
    }

    return new_api, options


class MockGCalService:
    def __init__(self) -> None:
        self.active = True
        self._events: List[CalendarEvent] = []
        self._event_json: Dict[Any, Any] = {}
        self._cal_json: Dict[Any, Any] = {}

        self._first_event_call = False

    def get_events_for_date(self, date_today: date) -> List[CalendarEvent]:
        return self._events

    def calendarList(self) -> MockGCalFunc:
        return MockGCalFunc(self._cal_json)

    def events(self) -> MockGCalFunc:

        if self._first_event_call:
            return MockGCalFunc({"items": []})

        self._first_event_call = True
        return MockGCalFunc(self._event_json)


class MockGCalFunc:
    def __init__(self, input_json: Dict[Any, Any]) -> None:
        self._json_response: Dict[Any, Any] = input_json

    def list(self, **_: List[Any]) -> MockGCalFunc:
        sub_func = MockGCalFunc(self._json_response)
        return sub_func

    def execute(self) -> Dict[Any, Any]:
        return self._json_response
