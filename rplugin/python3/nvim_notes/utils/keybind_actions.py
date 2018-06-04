import re

from nvim_notes.helpers.markdown_helpers import get_start_of_line
from nvim_notes.utils.constants import (BULLET_POINT_REGEX, CHECKED_TODO,
                                        EMPTY_TODO, PADDING, STRIKEDOUT,
                                        STRIKEOUT)


def pick_action(line):
    """pick_action

    Given a line, pick the appropriate toggleable action.
    """

    if EMPTY_TODO in line or CHECKED_TODO in line:
        return toggle_todo(line)

    return strikeout_line(line)


def strikeout_line(line):
    """strikeout_line

    Strikeout a given line.
    """

    line_already_striked_out = re.findall(STRIKEDOUT, line)
    line_not_bullet_point = re.findall(BULLET_POINT_REGEX, line)

    if line_already_striked_out:
        return [line.replace(STRIKEOUT, '')]

    if line_not_bullet_point:
        return [line]

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
