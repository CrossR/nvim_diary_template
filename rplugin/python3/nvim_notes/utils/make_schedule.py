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


def format_events_line(event):
    """format_events_line

    Given an event, will produce a formatted line for that event.
    """

    # TODO: Make the format strings here into a config option.
    start_time = get_time(event['start_time']).strftime(DATETIME_FORMAT)
    end_time = get_time(event['end_time']).strftime(DATETIME_FORMAT)
    event_name = event['event_name']

    # TODO: Similarly, make this string into a config option.
    return f"    - {start_time} - {end_time}: {event_name}"

def produce_schedule_markdown(event_list):
    """produce_schedule_markdown

    Given a list of events, will produce a basic bit of markdown
    to display that event.
    """

    markdown_lines = []

    # TODO: Should probably swap this to be a config option,
    # something like f"{importance * #}".
    markdown_lines.append("# Schedule")

    for event in event_list:
        current_schedule_line = format_events_line(event)
        markdown_lines.append(current_schedule_line)

    return markdown_lines

def make_schedule(nvim, options):
    """make_schedule

    A wrapper function to make a schedule for the current day.
    """

    todays_events = []

    if options.use_google_calendar:
        calendar_events = get_events_for_day(nvim, options)

        if calendar_events is not None:
            todays_events.extend(calendar_events)

    markdown = produce_schedule_markdown(todays_events)

    return markdown
