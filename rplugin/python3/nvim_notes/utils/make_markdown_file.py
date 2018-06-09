"""make_markdown_file

Functions to open the markdown files from the filesystem, or make them if
they don't exist.
"""

from datetime import date, timedelta
from os import makedirs, path

from nvim_notes.helpers.neovim_helpers import open_file, set_buffer_contents
from nvim_notes.utils.constants import FILE_TYPE
from nvim_notes.utils.make_schedule import produce_schedule_markdown
from nvim_notes.utils.make_todos import get_past_todos


def open_todays_schedule(nvim, options, gcal_service):
    """open_todays_schedule

    Open the actual schedule markdown file.
    This includes the following steps:
        * Open the file if it already exists.
        * If not, put the default template in and save.
    """

    todays_file = get_schedule_file_path_for_date(
        options.notes_path,
        date.today()
    )

    # If the file exists, then it much already exist so we don't need to
    # build it up. However, we want to open it regardless, so if not, the
    # new markdown is saved in the correct place, and opened in the correct
    # way.

    open_file(nvim, todays_file, options.open_method)

    if path.isfile(todays_file):
        return

    full_markdown = []

    full_markdown.extend(generate_markdown_metadata())

    for heading in options.headings:
        full_markdown.append(f"# {heading}")
        full_markdown.append("")

    # Bring over old ToDos.
    rolled_over_todos = get_past_todos(options)
    full_markdown.extend(rolled_over_todos)

    # Add in Todays Calendar Entries
    todays_events = gcal_service.todays_events
    schedule_markdown = produce_schedule_markdown(todays_events)
    full_markdown.extend(schedule_markdown)

    makedirs(path.dirname(todays_file), exist_ok=True)
    open_file(nvim, todays_file, options.open_method)

    set_buffer_contents(nvim, full_markdown)
    nvim.command(":w")


def get_schedule_file_path_for_date(notes_path, passed_date):
    """get_schedule_file_path_for_date

    Gets the file path for the given schedule file.
    """

    return path.join(
        notes_path,
        passed_date.strftime("%Y"),
        passed_date.strftime("%B"),
        str(passed_date) + FILE_TYPE
    )


def generate_markdown_metadata():
    """generate_markdown_metadata

    Add some basic metadata to the stop of the file
    in HTML tags.
    """

    metadata = []

    metadata.append("<!---")
    metadata.append(f"    Date: {date.today()}")
    metadata.append(f"    Tags:")
    metadata.append("--->")
    metadata.append("")

    return metadata


def open_schedule_file(nvim, options, day_delta):
    """open_schedule_file

    Open a given schedule file with a day delta.
    That is, a day_delta of -1 would open the schedule
    from yesterday, 0 would be today, and +1 tomorrow.
    """

    specified_date = date.today() + timedelta(days=day_delta)

    schedule_file_name = get_schedule_file_path_for_date(
        options.notes_path,
        specified_date
    )

    if not open_file(nvim, schedule_file_name):
        nvim.err_write(
            f"No schedule file exists for {specified_date}."
        )
