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


def get_start_of_line(line: str) -> str:
    """get_start_of_line

    Return the start of a given line.
    """

    first_non_space: int = len(line) - len(line.strip())
    start_of_line: str = line[: first_non_space + 1]

    return start_of_line


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


def split_line(line: str) -> List[str]:
    """split_line

    Splits a line at 79 characters, such that it can be wrapped.
    """

    if len(line) <= 79:
        return [line]

    reversed_line: str = line[:80][::-1]
    space_index: int = reversed_line.find(" ")

    before_space_index: int = 80 - space_index - 1
    after_space_index: int = 80 - space_index

    lines: List[str] = [line[:before_space_index]]

    padding: int = get_line_padding(line)
    line_remainder: str = apply_padding(line[after_space_index:], padding)

    return lines + split_line(line_remainder)


def get_line_padding(line: str) -> int:
    """get_line_padding

    Return the indentation of the line before the bullet.
    """

    return len(line) - len(line.lstrip(" "))


def apply_padding(line: str, padding: int) -> str:
    """apply_padding

    Adds the required number of spaces to the current line.
    """

    return f"{padding * ' '}{line}"
