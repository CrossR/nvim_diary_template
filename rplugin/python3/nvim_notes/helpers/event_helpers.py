from operator import itemgetter

from dateutil import parser


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
