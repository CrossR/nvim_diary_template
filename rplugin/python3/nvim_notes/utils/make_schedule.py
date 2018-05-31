from .helpers import convert_events

def format_events_lines(events):
    """format_events_lines

    Given some events, will produce formatted lines for them.
    """

    events_lines = []

    simplified_events = convert_events(events)

    for event in simplified_events:

        start_time = event['start_time']
        end_time = event['end_time']
        event_name = event['event_name']

        # TODO: Similarly, make this string into a config option.
        current_line = f"* {start_time} - {end_time}: {event_name}"

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
    markdown_lines.append("# Schedule")

    schedule_lines = format_events_lines(event_list)
    markdown_lines.extend(schedule_lines)

    return markdown_lines