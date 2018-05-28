from .make_schedule import make_schedule

# TODO: Plug this in as a config option
HEADINGS = ['Notes', 'Issues', 'ToDo']

def produce_daily_markdown(options,
                           headings=HEADINGS):
    full_markdown_file = []

    for heading in headings:
        full_markdown_file.append(f"# {heading}")
        full_markdown_file.append("\n")

    full_markdown_file.extend(make_schedule(options))

    return full_markdown_file