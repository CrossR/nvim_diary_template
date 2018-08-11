"""google_calendar_helpers

Simple helpers to deal with Google calendar, and the replies it sends.
"""
from datetime import datetime
from typing import Any, Dict, List, Union

from dataclasses import is_dataclass
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


def get_time(time_to_convert: str) -> datetime:
    """get_time

    Time object parser for Google Calendar responses.

    Since the Google API response can either be a 'dateTime' or
    'date' object depending on if the event is timed, or the whole day,
    we need to parse and return the object differently for each.
    """

    parsed_datetime: datetime = parser.parse(time_to_convert)

    return parsed_datetime


def format_google_events(events_list: List[Dict[str, Any]]) -> List[CalendarEvent]:
    """format_google_events

    Formats a list of GCal events down to the event name, and the
    start and end date of the event.
    """

    filtered_events: List[CalendarEvent] = []

    for event in events_list:
        filtered_events.append(
            CalendarEvent(
                name=event["summary"],
                start=event["start"]["dateTime"],
                end=event["end"]["dateTime"],
            )
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


def get_calendar_objects(
    events: Union[List[CalendarEvent], List[Dict[str, Any]]]
) -> List[CalendarEvent]:
    """get_calendar_objects

    Convert the loaded dicts to Objects, if they are not already.
    This is easier for a number of reasons, the main of which is
    that naming is kept consistent, versus dicts which require more
    careful usage.
    """

    events_to_convert: List[Dict[str, Any]] = [
        event for event in events if isinstance(event, dict)
    ]

    # TODO: Update this to use `is_dataclass` when we swap to Python 3.7
    event_objects: List[CalendarEvent] = [
        event for event in events if not isinstance(event, dict)
    ]

    for event in events_to_convert:
        event_objects.append(
            CalendarEvent(name=event["name"], start=event["start"], end=event["end"])
        )

    return event_objects
