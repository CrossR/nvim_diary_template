from nvim_notes.helpers.event_helpers import sort_events
from nvim_notes.utils.constants import TIME_FORMAT
from nvim_notes.utils.parse_markdown import parse_markdown_file_for_events
from nvim_notes.utils.make_schedule import set_schedule_from_events_list


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
