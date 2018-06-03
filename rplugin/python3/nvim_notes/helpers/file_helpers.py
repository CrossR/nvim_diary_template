import glob
from os import path

from nvim_notes.utils.constants import FILE_TYPE_WILDCARD


def get_past_notes(options):
    """get_past_notes

    Get the past notes file, and return the specified amount.
    """

    days_to_check = options.days_to_roll_over

    event_files = path.join(
        options.notes_path,
        "*",
        "*",
        FILE_TYPE_WILDCARD
    )

    files = glob.glob(event_files)
    file_names = sorted([path.basename(x) for x in files])

    if len(file_names) < days_to_check:
        return file_names
    else:
        return file_names[:days_to_check]


def get_note_file_content(file_path):
    """get_note_file_content

    Return the content of the passed note file.
    """

    with open(file_path) as f:
        return f.read()


def get_note_path(options, note_name):
    """get_note_path

    Gives a full path, given just a note name.
    """
    pattern = path.join(
        options.notes_path,
        "*",
        "*",
        note_name
    )

    return glob.glob(pattern)[0]
