from os import path

from dateutil import parser

from .google_cal_integration import get_events_for_day

DATETIME_FORMAT = "%d/%m/%Y %H:%M"

def get_time(time_dict):
    """get_time

    Since the Google API response can either be a 'dateTime' or
    'date' object depending on if the event is timed, or the whole day,
    we need to parse and return the object differently for each.
    """

    try:
        datetime_obj = parser.parse(time_dict['dateTime'])
    except KeyError:
        datetime_obj = parser.parse(time_dict['date'])

    return datetime_obj

def convert_events(events):
    """convert_events

    Given a list of events, convert the time objects to a human readable
    form.
    """

    formatted_events = []

    for event in events:
        # TODO: Make the format strings here into a config option.
        start_time = get_time(event['start_time']).strftime(DATETIME_FORMAT)
        end_time = get_time(event['end_time']).strftime(DATETIME_FORMAT)
        event_name = event['event_name']

        formatted_events.append({
            'event_name': event_name,
            'start_time': start_time,
            'end_time': end_time
        })

    return formatted_events


def format_events_lines(events):
    """format_events_lines

    Given an event, will produce a formatted line for that event.
    """

    events_lines = []

    simplified_events = convert_events(events)

    for event in simplified_events:

        start_time = event['start_time']
        end_time = event['end_time']
        event_name = event['event_name']

        # TODO: Similarly, make this string into a config option.
        current_line = f"    - {start_time} - {end_time}: {event_name}"

        events_lines.append(current_line)

    return events_lines

def produce_schedule_markdown(event_list):
    """produce_schedule_markdown

    Given a list of events, will produce a basic bit of markdown
    to display that event.
    """

    markdown_lines = []

    # TODO: Should probably swap this to be a config option,
    # something like f"{importance * #}".
    markdown_lines.append("# Schedule")

    current_schedule_line = format_events_lines(event_list)
    markdown_lines.append(current_schedule_line)

    return markdown_lines

def make_schedule(nvim, options, todays_events = []):
    """make_schedule

    A wrapper function to make a schedule for the current day.
    """

    markdown = produce_schedule_markdown(todays_events)

    return markdown
