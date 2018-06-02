import glob
from os import path

from nvim_notes.utils.constants import TODO_IS_CHECKED, TODO_NOT_CHECKED
from nvim_notes.utils.parse_markdown import parse_markdown_file_for_todos


def get_ongoing_todos(nvim, options):
    days_to_check = options.days_to_roll_over

    event_files = path.join(
        options.notes_path,
        "*",
        "*",
        "*.md"
    )

    files = glob.glob(event_files)

    return files[:days_to_check]
