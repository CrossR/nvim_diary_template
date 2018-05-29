from .make_schedule import make_schedule

def produce_daily_markdown(options):
    """produce_daily_markdown

    Produce the actual markdown that is shown on the page.
    """

    full_markdown_file = []

    for heading in options.headings:
        full_markdown_file.append(f"# {heading}")
        full_markdown_file.append("")

    full_markdown_file.extend(make_schedule(options))

    return full_markdown_file
