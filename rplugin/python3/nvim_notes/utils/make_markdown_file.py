import re
from datetime import date
from os import path

from .make_schedule import produce_schedule_markdown

DATE_REGEX = r"[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}"
EVENT_REGEX = r"(?<=: ).*$"


def make_markdown_file(nvim, options, gcal_service):
    """make_markdown_file

    Produce the actual markdown file.
    """
    todays_file = path.join(
        options.notes_path,
        date.today().strftime("%Y"),
        date.today().strftime("%B"),
        str(date.today()),
        ".md"
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

    open_file(nvim, todays_file, options.open_method)

    new_buffer_number = nvim.current.buffer.number

    nvim.api.buf_set_lines(
        new_buffer_number,
        0,
        -1,
        True,
        full_markdown
    )

    nvim.command(":w")


def open_file(nvim, path, open_method):
    nvim.command(f":{open_method} {path}")


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
        parsed_event_line = re.findall(DATE_REGEX, event)

        start_date = parsed_event_line[0]
        end_date = parsed_event_line[1]
        event_details = re.search(EVENT_REGEX, event)[0]

        event_dict = {
            'event_name': event_details,
            'start_time': start_date,
            'end_time': end_date
        }

        formatted_events.append(event_dict)

    return formatted_events


def parse_markdown_file_for_events(nvim):
    """parse_markdown_file_for_events

    Gets the contents of the current NeoVim buffer,
    and parses the schedule section into events.
    """

    buffer_number = nvim.current.buffer.number
    current_buffer_contents = nvim.api.buf_get_lines(
        buffer_number,
        0,
        -1,
        True
    )

    # Do the search in reverse since we know the schedule comes last
    for line_index, line in enumerate(reversed(current_buffer_contents)):
        if line == '# Schedule':
            buffer_events_index = line_index

    buffer_events_index = len(current_buffer_contents) - buffer_events_index
    events = current_buffer_contents[buffer_events_index:]
    formatted_events = parse_buffer_events(events)

    return formatted_events
