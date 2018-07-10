"""markdown_helpers

Simple helpers to help deal with parsed markdown lines.
"""

from nvim_diary_template.helpers.event_helpers import sort_events
from nvim_diary_template.utils.constants import TIME_FORMAT
from nvim_diary_template.utils.parse_markdown import parse_markdown_file_for_events
from nvim_diary_template.utils.make_schedule import set_schedule_from_events_list


def get_start_of_line(line):
    """get_start_of_line

    Return the start of a given line.
    """

    first_non_space = len(line) - len(line.strip())
    start_of_line = line[:first_non_space + 1]

    return start_of_line


def sort_markdown_events(nvim):
    """sort_markdown_events

    Given the markdown file, will sort the events currently
    in the file and then update them in place.
    """

    unsorted_events = parse_markdown_file_for_events(nvim, TIME_FORMAT)
    sorted_events = sort_events(unsorted_events)

    # If its already sorted, return to stop any API calls.
    if sorted_events == unsorted_events:
        return

    set_schedule_from_events_list(nvim, sorted_events, True)


def split_line(line):
    """split_line

    Splits a line at 79 characters, such that it can be wrapped.
    """

    if len(line) <= 79:
        return [line]

    reversed_line = line[:80][::-1]
    space_index = reversed_line.find(' ')

    before_space_index = 80 - space_index - 1
    after_space_index = 80 - space_index

    lines = [line[:before_space_index]]

    padding = get_line_padding(line)
    line_remainder = apply_padding(line[after_space_index:], padding)

    return lines + split_line(line_remainder)


def get_line_padding(line):
    """get_line_padding

    Return the indentation of the line before the bullet.
    """

    return len(line) - len(line.lstrip(' '))


def apply_padding(line, padding):
    """apply_padding

    Adds the required number of spaces to the current line.
    """

    return f"{padding * ' '}{line}"
