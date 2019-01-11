"""markdown_helpers

Simple helpers to help deal with parsed markdown lines.
"""

from typing import List

from neovim import Nvim

from ..classes.calendar_event_class import CalendarEvent
from ..helpers.event_helpers import sort_events
from ..utils.constants import TIME_FORMAT
from ..utils.make_schedule import set_schedule_from_events_list
from ..utils.parse_markdown import parse_markdown_file_for_events


def sort_markdown_events(nvim: Nvim) -> None:
    """sort_markdown_events

    Given the markdown file, will sort the events currently
    in the file and then update them in place.
    """

    unsorted_events: List[CalendarEvent] = parse_markdown_file_for_events(
        nvim, TIME_FORMAT
    )
    sorted_events: List[CalendarEvent] = sort_events(unsorted_events)

    # If its already sorted, return to stop any API calls.
    if sorted_events == unsorted_events:
        return

    set_schedule_from_events_list(nvim, sorted_events, True)


def format_markdown_events(nvim: Nvim) -> None:
    """format_markdown_events

    Given the markdown file, will format the events
    in the file and then update them in place.

    This is also used to remove any extra metadata once it has been used.
    """

    unsorted_events: List[CalendarEvent] = parse_markdown_file_for_events(
        nvim, TIME_FORMAT
    )
    sorted_events: List[CalendarEvent] = sort_events(unsorted_events)

    set_schedule_from_events_list(nvim, sorted_events, True)
