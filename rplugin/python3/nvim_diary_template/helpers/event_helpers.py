"""event_helpers

Simple helpers to deal with parsed events.
"""

from dateutil import parser

from nvim_diary_template.classes.calendar_event_class import CalendarEvent


def sort_events(events):
    """sort_events

    Given a list of events, sort them by their start time first,
    then end time and finally event name.
    """

    return sorted(events, key=lambda e: (e.start, e.end, e.name))


def format_event(event, format_string):
    """format_event

    Simple helper function to format an event to a given format.
    """

    start_time = parser.parse(event.start).strftime(format_string)
    end_time = parser.parse(event.end).strftime(format_string)

    return CalendarEvent(name=event.name, start=start_time, end=end_time)
