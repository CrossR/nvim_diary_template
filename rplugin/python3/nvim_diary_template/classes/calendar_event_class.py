# pylint: disable=all
"""calendar_event_class

A simple Dataclass to store Calendar events.
"""
from dataclasses import dataclass


@dataclass
class CalendarEvent:
    """CalendarEvent

    A simple Dataclass to store a Calendar event.
    """

    name: str
    start: str
    end: str
    calendar: str = ""
