"""make_schedule

Functions to build and parse the schedule section of the markdown.
"""

from nvim_notes.helpers.google_calendar_helpers import convert_events
from nvim_notes.helpers.neovim_helpers import (get_buffer_contents,
                                               get_section_line)
from nvim_notes.utils.constants import (BULLET_POINT, SCHEDULE_HEADING,
                                        TIME_FORMAT)


def format_events_lines(events):
    """format_events_lines

    Given some events, will produce formatted lines for them.
    """

    events_lines = []

    for event in events:

        start = event['start_time']
        end = event['end_time']
        event = event['event_name']

        # TODO: Similarly, make this string into a config option.
        current_line = f"{BULLET_POINT}   {start} - {end}: {event}"

        events_lines.append(current_line)

    events_lines.append("")

    return events_lines


def produce_schedule_markdown(event_list):
    """produce_schedule_markdown

    Given a list of events, will produce a basic bit of markdown
    to display that event.
    """

    markdown_lines = []

    # TODO: Should probably swap this to be a config option,
    # something like f"{importance * #}".
    markdown_lines.append(SCHEDULE_HEADING)

    converted_events = convert_events(event_list, TIME_FORMAT)
    schedule_lines = format_events_lines(converted_events)
    markdown_lines.extend(schedule_lines)

    return markdown_lines


def set_schedule_from_events_list(nvim, events, strict_indexing):
    """set_schedule_from_events_list

    Update the schedule for the current buffer with a new list of events.
    """

    event_lines = format_events_lines(events)

    buffer_number = nvim.current.buffer.number
    current_buffer = get_buffer_contents(nvim)

    # We want the line after, as this gives the line of the heading.
    # Then add one to the end to replace the newline, as we add one.
    old_events_start_line = get_section_line(
        current_buffer,
        SCHEDULE_HEADING
    ) + 1

    old_events_end_line = old_events_start_line + len(events) + 1

    nvim.api.buf_set_lines(
        buffer_number,
        old_events_start_line,
        old_events_end_line,
        strict_indexing,
        event_lines
    )
