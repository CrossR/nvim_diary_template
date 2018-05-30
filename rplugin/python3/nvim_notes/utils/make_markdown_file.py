from .make_schedule import make_schedule

def produce_daily_markdown(nvim, options):
    """produce_daily_markdown

    Produce the actual markdown that is shown on the page.
    """

    full_markdown_file = []

    for heading in options.headings:
        full_markdown_file.append(f"# {heading}")
        full_markdown_file.append("")

    full_markdown_file.extend(make_schedule(nvim, options))

    return full_markdown_file

def parse_buffer_events(events):
    formatted_events = []

    for event in events:
        if event == '':
            continue

        format_string = f"    - {start_time} - {end_time}: {event_name}"


def parse_markdown_file_for_events(nvim):
    buffer_number = nvim.current.buffer.number
    current_buffer_contents = nvim.api.buf_get_lines(
        buffer_number,
        0,
        -1,
        True
    )

    # Do the search in reverse since we know the schdule comes last
    for line_index, line in enumerate(reversed(current_buffer_contents)):
        if line == '# Schedule':
            buffer_events_index = line_index

    buffer_events_index = len(current_buffer_contents) - buffer_events_index
    events = current_buffer_contents[buffer_events_index:]
    formatted_events = parse_buffer_events(events)

