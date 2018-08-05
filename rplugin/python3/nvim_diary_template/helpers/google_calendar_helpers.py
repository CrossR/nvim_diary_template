"""google_calendar_helpers

Simple helpers to deal with Google calendar, and the replies it sends.
"""

from dateutil import parser


def convert_events(events, format_string):
    """convert_events

    Given a list of events, convert the time objects to a human
    readable form.
    """

    formatted_events = []

    for event in events:
        # TODO: Make the format strings here into a config option.
        start_time = get_time(event["start_time"]).strftime(format_string)
        end_time = get_time(event["end_time"]).strftime(format_string)
        event_name = event["event_name"]

        formatted_events.append(
            {"event_name": event_name, "start_time": start_time, "end_time": end_time}
        )

    return formatted_events


def get_time(time_dict):
    """get_time

    Time object parser for Google Calendar responses.

    Since the Google API response can either be a 'dateTime' or
    'date' object depending on if the event is timed, or the whole day,
    we need to parse and return the object differently for each.
    """

    try:
        datetime_obj = parser.parse(time_dict["dateTime"])
    except KeyError:
        datetime_obj = parser.parse(time_dict["date"])

    return datetime_obj


def format_google_events(events_list):
    """format_google_events

    Formats a list of GCal events down to the event name, and the
    start and end date of the event.
    """

    filtered_events = []

    for event in events_list:
        event_dict = {
            "event_name": event["summary"],
            "start_time": event["start"],
            "end_time": event["end"],
        }

        filtered_events.append(event_dict)

    return filtered_events


def create_google_event(event, timezone):
    """create_google_event

    Given an event, create a Google Event with a time zone.
    """

    return {
        "summary": event["event_name"],
        "start": {
            "timeZone": timezone,
            "dateTime": parser.parse(event["start_time"]).isoformat(),
        },
        "end": {
            "timeZone": timezone,
            "dateTime": parser.parse(event["end_time"]).isoformat(),
        },
    }
