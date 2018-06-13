"""keybind_actions

Functions for Neovim keybind actions and picking between them.
"""

import re

from nvim_notes.helpers.markdown_helpers import get_start_of_line
from nvim_notes.helpers.neovim_helpers import (get_line_content,
                                               get_multi_line_bullet,
                                               set_line_content)
from nvim_notes.utils.constants import (BULLET_POINT_REGEX, CHECKED_TODO,
                                        EMPTY_TODO, PADDING, STRIKEOUT,
                                        STRUCK_OUT)


def pick_action(nvim):
    """pick_action

    Given a line, pick the appropriate toggleable action.
    """

    line = get_line_content(nvim)

    if EMPTY_TODO in line or CHECKED_TODO in line:
        updated_lines = toggle_todo(line)
    else:
        lines = get_multi_line_bullet(nvim)
        updated_lines = strikeout_lines(lines)

    set_line_content(
        nvim,
        updated_lines,
        line_offset=len(updated_lines)
    )


def strikeout_lines(lines):
    """strikeout_lines

    Strikeout some given lines.
    """

    # TODO: Check this logic. Currently, only the first line is checked, when
    # the remaining lines could be different.
    line_contains_bullet_point = re.findall(BULLET_POINT_REGEX, lines[0])
    line_already_struck_out = re.findall(STRUCK_OUT, lines[0])

    if not line_contains_bullet_point:
        return lines

    if line_already_struck_out:
        return [
            line.replace(STRIKEOUT, '') for line in lines
        ]

    replacement_lines = []

    # The first line includes the bullet point, so we need this.
    line_content = lines[0].strip().split()[1:]
    start_of_line = get_start_of_line(lines[0])
    new_line = f"{start_of_line}{PADDING}~~{' '.join(line_content)}~~"

    replacement_lines.append(new_line)

    # For the rest, the new line will look a little different. Since there is
    # now no bullet, we use the full line rather than [1:] On the other hand,
    # get_start_of_line will now return the spaces and the first character of
    # the sentence, so we must skip this character, by ignoring the last
    # character.
    for line in lines[1:]:
        line_content = line.strip().split()
        start_of_line = get_start_of_line(line)
        new_line = f"{start_of_line[:-1]}~~{' '.join(line_content)}~~"
        replacement_lines.append(new_line)

    return replacement_lines


def toggle_todo(line):
    """toggle_todo

    Given a todo, toggle it off.
    """

    if EMPTY_TODO in line:
        return [line.replace(EMPTY_TODO, CHECKED_TODO)]
    elif CHECKED_TODO in line:
        return [line.replace(CHECKED_TODO, EMPTY_TODO)]

    return [line]
