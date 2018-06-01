from operator import itemgetter
from os import path

from dateutil import parser

DATETIME_FORMAT = "%d/%m/%Y %H:%M"
TIME_FORMAT = "%H:%M"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

def get_time(time_dict):
    """get_time

    Time object parser for Google Calendar responses.

    Since the Google API response can either be a 'dateTime' or
    'date' object depending on if the event is timed, or the whole day,
    we need to parse and return the object differently for each.
    """

    try:
        datetime_obj = parser.parse(time_dict['dateTime'])
    except KeyError:
        datetime_obj = parser.parse(time_dict['date'])

    return datetime_obj


def convert_events(events, format_string):
    """convert_events

    Given a list of events, convert the time objects to a human readable
    form.
    """

    formatted_events = []

    for event in events:
        # TODO: Make the format strings here into a config option.
        start_time = get_time(event['start_time']).strftime(format_string)
        end_time = get_time(event['end_time']).strftime(format_string)
        event_name = event['event_name']

        formatted_events.append({
            'event_name': event_name,
            'start_time': start_time,
            'end_time': end_time
        })

    return formatted_events


def format_google_events(events_list):
    """format_google_events

    Formats a list of GCal events down to the event name, and the
    start and end date of the event.
    """

    filtered_events = []

    for event in events_list:
        event_dict = {
            'event_name': event['summary'],
            'start_time': event['start'],
            'end_time': event['end']
        }

        filtered_events.append(event_dict)

    return filtered_events


def create_google_event(event, timezone):
    return {
        "summary": event['event_name'],
        "start": {
            "timeZone": timezone,
            "dateTime": parser.parse(event['start_time']).isoformat()
        },
        "end": {
            "timeZone": timezone,
            "dateTime": parser.parse(event['end_time']).isoformat()
        }
    }


def open_file(nvim, path, open_method):
    """open_file

    Opens the file in the specified way.
    """

    nvim.command(f":{open_method} {path}")


def sort_events(events):
    """sort_events

    Given a list of events, sort them by their start time first,
    then end time and finally event name.
    """
    return sorted(
        events,
        key=itemgetter('start_time', 'end_time', 'event_name')
    )


def format_event(event, format_string):
    """format_event

    Simple helper function to format an event to a given format.
    """

    start_time = parser.parse(event['start_time']).strftime(format_string)
    end_time = parser.parse(event['end_time']).strftime(format_string)
    event_name = event['event_name']

    return {
        'event_name': event_name,
        'start_time': start_time,
        'end_time': end_time
    }


def get_schedule_section_line(buffer_contents):
    """get_schedule_section_line

    Given a buffer, get the line that the schedule section starts on.
    """

    buffer_events_index = -1

    # Do the search in reverse since we know the schedule comes last
    for line_index, line in enumerate(reversed(buffer_contents)):
        if line == '# Schedule':
            buffer_events_index = line_index

    buffer_events_index = len(buffer_contents) - buffer_events_index

    return buffer_events_index


def get_buffer_contents(nvim):
    """get_buffer_contents

    Get the contents of the current buffer.
    """

    buffer_number = nvim.current.buffer.number

    return nvim.api.buf_get_lines(
        buffer_number,
        0,
        -1,
        True
    )


def set_buffer_contents(nvim, data):
    """set_buffer_contents

    Set the contents of the current buffer.
    """
    buffer_number = nvim.current.buffer.number

    nvim.api.buf_set_lines(
        buffer_number,
        0,
        -1,
        True,
        data
    )


def get_line_content(nvim):
    """get_line_content

    Get the contents of the current line.
    """

    buffer_number = nvim.current.buffer.number
    cursor_line = nvim.current.window.cursor[0]

    return nvim.api.buf_get_lines(
        buffer_number,
        cursor_line - 1,
        cursor_line,
        True
    )[0]


def set_line_content(nvim, data):
    """set_line_content

    Set the contents of the current line.
    """
    buffer_number = nvim.current.buffer.number
    cursor_line = nvim.current.window.cursor[0]

    nvim.api.buf_set_lines(
        buffer_number,
        cursor_line - 1,
        cursor_line,
        True,
        data
    )
