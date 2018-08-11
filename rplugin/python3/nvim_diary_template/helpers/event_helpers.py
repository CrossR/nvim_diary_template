"""event_helpers

Simple helpers to deal with parsed events.
"""

from typing import List

from dateutil import parser

from ..classes.calendar_event_class import CalendarEvent


def sort_events(events: List[CalendarEvent]) -> List[CalendarEvent]:
    """sort_events

    Given a list of events, sort them by their start time first,
    then end time and finally event name.
    """

    return sorted(events, key=lambda e: (e.start, e.end, e.name))


def format_event(event: CalendarEvent, format_string: str) -> CalendarEvent:
    """format_event

    Simple helper function to format an event to a given format.
    """

    start_time: str = parser.parse(event.start).strftime(format_string)
    end_time: str = parser.parse(event.end).strftime(format_string)

    return CalendarEvent(name=event.name, start=start_time, end=end_time)
