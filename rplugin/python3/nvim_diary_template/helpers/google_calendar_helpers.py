"""google_calendar_helpers

Simple helpers to deal with Google calendar, and the replies it sends.
"""
from datetime import datetime
from typing import Any, Dict, List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent


def convert_events(
    events: List[CalendarEvent], format_string: str
) -> List[CalendarEvent]:
    """convert_events

    Given a list of events, convert the time objects to a human
    readable form.
    """

    formatted_events: List[CalendarEvent] = []

    for event in events:
        start_time: str = get_time(event.start).strftime(format_string)
        end_time: str = get_time(event.end).strftime(format_string)

        formatted_events.append(
            CalendarEvent(name=event.name, start=start_time, end=end_time)
        )

    return formatted_events


def get_time(time_dict: Dict[str, str]) -> datetime:
    """get_time

    Time object parser for Google Calendar responses.

    Since the Google API response can either be a 'dateTime' or
    'date' object depending on if the event is timed, or the whole day,
    we need to parse and return the object differently for each.
    """

    try:
        datetime_obj: datetime = parser.parse(time_dict["dateTime"])
    except KeyError:
        datetime_obj = parser.parse(time_dict["date"])

    return datetime_obj


def format_google_events(events_list: List[Dict[str, str]]) -> List[CalendarEvent]:
    """format_google_events

    Formats a list of GCal events down to the event name, and the
    start and end date of the event.
    """

    filtered_events: List[CalendarEvent] = []

    for event in events_list:
        filtered_events.append(
            CalendarEvent(name=event["summary"], start=event["start"], end=event["end"])
        )

    return filtered_events


def create_google_event(event: CalendarEvent, timezone: str) -> Dict[str, Any]:
    """create_google_event

    Given an event, create a Google Event with a time zone.
    """

    return {
        "summary": event.name,
        "start": {
            "timeZone": timezone,
            "dateTime": parser.parse(event.start).isoformat(),
        },
        "end": {"timeZone": timezone, "dateTime": parser.parse(event.end).isoformat()},
    }
