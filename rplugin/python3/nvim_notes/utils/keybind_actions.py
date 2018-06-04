from nvim_notes.helpers.markdown_helpers import get_start_of_line
from nvim_notes.utils.constants import CHECKED_TODO, EMPTY_TODO, PADDING


def strikeout_line(line):
    """strikeout_line

    Strikeout a given line.
    """
    line_content = line.strip().split()[1:]
    start_of_line = get_start_of_line(line)

    return [f"{start_of_line}{PADDING}~~{' '.join(line_content)}~~"]


def toggle_todo(line):
    """toggle_todo

    Given a todo, toggle it off.
    """

    if EMPTY_TODO in line:
        return [line.replace(EMPTY_TODO, CHECKED_TODO)]
    elif CHECKED_TODO in line:
        return [line.replace(CHECKED_TODO, EMPTY_TODO)]

    return [line]
