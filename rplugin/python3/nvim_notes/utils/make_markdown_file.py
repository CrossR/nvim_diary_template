import re
from datetime import date
from os import makedirs, path

from dateutil import parser

from .helpers import (DATETIME_FORMAT, format_event, get_buffer_contents,
                      get_schedule_section_line, open_file,
                      set_buffer_contents, sort_events)
from .make_schedule import (format_events_lines, produce_schedule_markdown,
                            set_schedule_from_events_list)

DATETIME_REGEX = r"[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4} [0-9]{1,2}:[0-9]{1,2}"
TIME_REGEX = r"[0-9]{1,2}:[0-9]{1,2}"
EVENT_REGEX = r"(?<=: ).*$"


def open_markdown_file(nvim, options, gcal_service):
    """open_markdown_file

    Open the actual markdown file.
    This includes the following steps:
        * Open the file if it already exists.
        * If not, put the default template in and save.
    """
    todays_file = path.join(
        options.notes_path,
        date.today().strftime("%Y"),
        date.today().strftime("%B"),
        str(date.today()) + ".md"
    )

    if path.isfile(todays_file):
        open_file(nvim, todays_file, options.open_method)
        return

    full_markdown = []

    full_markdown.extend(generate_markdown_metadata())

    for heading in options.headings:
        full_markdown.append(f"# {heading}")
        full_markdown.append("")

    todays_events = gcal_service.todays_events
    schedule_markdown = produce_schedule_markdown(todays_events)
    full_markdown.extend(schedule_markdown)

    makedirs(path.dirname(todays_file), exist_ok=True)
    open_file(nvim, todays_file, options.open_method)

    set_buffer_contents(nvim, full_markdown)
    nvim.command(":w")


def generate_markdown_metadata():
    """generate_markdown_metadata

    Add some basic metadata to the stop of the file
    in HTML tags.
    """

    metadata = []

    metadata.append("<!---")
    metadata.append(f"    Date: {date.today()}")
    metadata.append(f"    Tags:")
    metadata.append("--->")
    metadata.append("")

    return metadata


def parse_buffer_events(events):
    """parse_buffer_events

    Given a list of events, parse the buffer lines and create event objects.
    """

    formatted_events = []

    for event in events:
        if event == '':
            continue

        # TODO: Regex is probably going to be a giant pain here,
        # and won't work if the string pattern changes.
        matches_date_time = re.findall(DATETIME_REGEX, event)

        if len(matches_date_time) > 0:
            matches_time = re.findall(TIME_REGEX, event)
            start_date = parser.parse(matches_time[0]) \
                               .strftime(DATETIME_FORMAT)
            end_date = parser.parse(matches_time[1]) \
                             .strftime(DATETIME_FORMAT)
        else:
            start_date = parser.parse(matches_date_time[0]) \
                               .strftime(DATETIME_FORMAT)
            end_date = parser.parse(matches_date_time[1]) \
                             .strftime(DATETIME_FORMAT)

        event_details = re.search(EVENT_REGEX, event)[0]

        event_dict = {
            'event_name': event_details,
            'start_time': start_date,
            'end_time': end_date
        }

        formatted_events.append(event_dict)

    return formatted_events


def sort_markdown_events(nvim):
    """sort_markdown_events

    Given the markdown file, will sort the events currently
    in the file and then update them in place.
    """

    unsorted_events = parse_markdown_file_for_events(nvim)
    sorted_events = sort_events(unsorted_events)

    # If its already sorted, return to stop any API calls.
    if sorted_events == unsorted_events:
        return

    set_schedule_from_events_list(nvim, sorted_events)


def parse_markdown_file_for_events(nvim):
    """parse_markdown_file_for_events

    Gets the contents of the current NeoVim buffer,
    and parses the schedule section into events.
    """

    current_buffer = get_buffer_contents(nvim)

    buffer_events_index = get_schedule_section_line(current_buffer)
    events = current_buffer[buffer_events_index:]
    formatted_events = parse_buffer_events(events)

    return formatted_events

def combine_markdown_and_calendar_events(nvim,
                                         markdown_events,
                                         google_events):
    buffer_events = [
        format_event(event, DATETIME_FORMAT) for event in markdown_events
    ]

    calendar_events = [
        format_event(event, DATETIME_FORMAT) for event in google_events
    ]

    combined_events = buffer_events
    combined_events.extend(
        event for event in calendar_events if event not in buffer_events
    )

    return combined_events
