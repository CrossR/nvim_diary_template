"""make_markdown_file

Functions to open the markdown files from the filesystem, or make them if
they don't exist.
"""

from datetime import date

from nvim_notes.helpers.neovim_helpers import set_buffer_contents
from nvim_notes.utils.make_schedule import produce_schedule_markdown
from nvim_notes.utils.make_todos import get_past_todos


def make_todays_diary(nvim, options, gcal_service):
    """make_todays_diary

    Make the actual diary markdown file.
    This includes the following steps:
        * Open the file if it already exists.
        * If not, put the default template in and save.
    """

    full_markdown = []

    diary_metadata = {
        "Date": str(date.today())
    }

    full_markdown.extend(generate_markdown_metadata(diary_metadata))

    for heading in options.daily_headings:
        full_markdown.append(f"# {heading}")
        full_markdown.append("")

    # Bring over old ToDos.
    rolled_over_todos = get_past_todos(options)
    full_markdown.extend(rolled_over_todos)

    # Add in Todays Calendar Entries
    todays_events = gcal_service.todays_events
    schedule_markdown = produce_schedule_markdown(todays_events)
    full_markdown.extend(schedule_markdown)

    set_buffer_contents(nvim, full_markdown)
    nvim.command(":w")


def generate_markdown_metadata(metadata_obj):
    """generate_markdown_metadata

    Add some basic metadata to the top of the file
    in HTML tags.
    """

    metadata = []

    metadata.append("<!---")

    passed_metadata = [
        f"    {key}: {value}" for key, value in metadata_obj.items()
    ]

    metadata.extend(passed_metadata)
    metadata.append(f"    Tags:")
    metadata.append("--->")
    metadata.append("")

    return metadata
