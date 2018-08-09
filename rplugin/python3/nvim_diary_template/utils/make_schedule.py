"""make_schedule

Functions to build and parse the schedule section of the markdown.
"""
from typing import List

from neovim import Nvim

from ..classes.calendar_event_class import CalendarEvent
from ..helpers.google_calendar_helpers import convert_events
from ..helpers.neovim_helpers import (
    get_buffer_contents,
    get_section_line,
)
from ..utils.constants import (
    BULLET_POINT,
    SCHEDULE_HEADING,
    TIME_FORMAT,
)


def format_events_lines(events: List[CalendarEvent]) -> List[str]:
    """format_events_lines

    Given some events, will produce formatted lines for them.
    """

    events_lines: List[str] = []

    for event in events:

        start: str = event.start
        end: str = event.end
        details: str = event.name

        current_line: str = f"{BULLET_POINT} {start} - {end}: {details}"

        events_lines.append(current_line)

    events_lines.append("")

    return events_lines


def produce_schedule_markdown(event_list: List[CalendarEvent]) -> List[str]:
    """produce_schedule_markdown

    Given a list of events, will produce a basic bit of markdown
    to display that event.
    """

    markdown_lines: List[str] = [SCHEDULE_HEADING, ""]

    converted_events: List[CalendarEvent] = convert_events(event_list, TIME_FORMAT)
    schedule_lines: List[str] = format_events_lines(converted_events)
    markdown_lines.extend(schedule_lines)

    return markdown_lines


def set_schedule_from_events_list(
    nvim: Nvim, events: List[CalendarEvent], strict_indexing: bool
):
    """set_schedule_from_events_list

    Update the schedule for the current buffer with a new list of events.
    """

    event_lines: List[str] = format_events_lines(events)

    buffer_number: int = nvim.current.buffer.number
    current_buffer: List[str] = get_buffer_contents(nvim)

    # We want the line after, as this gives the line of the heading.
    # Then add one to the end to replace the newline, as we add one.
    old_events_start_line: int = get_section_line(current_buffer, SCHEDULE_HEADING) + 1

    old_events_end_line: int = old_events_start_line + len(events) + 1

    nvim.api.buf_set_lines(
        buffer_number,
        old_events_start_line,
        old_events_end_line,
        strict_indexing,
        event_lines,
    )
