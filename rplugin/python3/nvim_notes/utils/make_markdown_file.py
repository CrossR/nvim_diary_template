"""make_markdown_file

Functions to open the markdown files from the filesystem, or make them if
they don't exist.
"""

from datetime import date, timedelta
from os import makedirs, path

from nvim_notes.helpers.neovim_helpers import (open_file, open_popup_file,
                                               set_buffer_contents)
from nvim_notes.utils.constants import FILE_TYPE, NOTE_FOLDER, SCHEDULE_FOLDER
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

    # If the file exists, open it and return.
    if path.isfile(todays_file):
        open_file(nvim, todays_file, options.open_method)
        return

    full_markdown = []

    schedule_metadata = {
        "Date": str(date.today())
    }

    full_markdown.extend(generate_markdown_metadata(schedule_metadata))

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
        SCHEDULE_FOLDER,
        passed_date.strftime("%Y"),
        passed_date.strftime("%B"),
        str(passed_date) + FILE_TYPE
    )


def get_note_file_path_for_topic(notes_path, passed_topic):
    """get_note_file_path_for_topic

    Gets the file path for the given note file.
    """

    return path.join(
        notes_path,
        NOTE_FOLDER,
        str(passed_topic) + FILE_TYPE
    )


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


def open_note_for_topic(nvim, options, note_topic):
    """open_note_for_topic

    Open the specified note markdown file.
    This includes the following steps:
        * Open the file if it already exists.
        * If not, put the default note template in and save.
    """

    note_file = get_note_file_path_for_topic(
        options.notes_path,
        note_topic
    )

    # If the file exists, open it and return.
    if path.isfile(note_file):
        open_file(nvim, note_file, options.open_method)
        return

    full_markdown = []

    note_metadata = {
        "Topic": note_topic
    }

    full_markdown.extend(generate_markdown_metadata(note_metadata))

    for heading in options.note_headings:
        full_markdown.append(f"# {heading}")
        full_markdown.append("")

    #TODO: Swap this open in pop somehow, I want both open in a new buffer and
    #also in a pop up one. Also need to add swapping to the note if its
    #already open, similarly for the schedules.
    makedirs(path.dirname(note_file), exist_ok=True)
    open_popup_file(nvim, note_file, options.pop_up_method)

    set_buffer_contents(nvim, full_markdown)
    nvim.command(":w")
