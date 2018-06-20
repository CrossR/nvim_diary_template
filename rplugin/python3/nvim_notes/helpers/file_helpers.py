"""file_helpers

Simple helpers to help with opening and finding files.
"""

import glob
from os import path

from nvim_notes.utils.constants import FILE_TYPE_WILDCARD, SCHEDULE_FOLDER


def get_past_schedules(options):
    """get_past_schedules

    Get past schedules files, and return the specified amount.
    """

    days_to_check = options.days_to_roll_over

    note_files = path.join(
        options.notes_path,
        SCHEDULE_FOLDER,
        "*",
        "*",
        FILE_TYPE_WILDCARD
    )

    files = glob.glob(note_files)
    file_names = sorted([path.basename(x) for x in files])

    if len(file_names) < days_to_check:
        return file_names

    return file_names[:days_to_check]


def get_file_content(file_path):
    """get_file_content

    Return the content of the passed note file.
    """

    with open(file_path) as note_file:
        return note_file.read().split('\n')


def get_schedule_path(options, note_name):
    """get_schedule_path

    Gives a full path, given just a schedule name.
    """
    pattern = path.join(
        options.notes_path,
        SCHEDULE_FOLDER,
        "*",
        "*",
        note_name
    )

    return glob.glob(pattern)[0]