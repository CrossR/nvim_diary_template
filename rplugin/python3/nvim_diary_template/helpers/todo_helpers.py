"""todo_helpers

Simple helpers for the markdown ToDos.
"""

import re

from nvim_notes.utils.constants import (BULLET_POINT, EMPTY_TODO,
                                        TODO_IS_CHECKED, TODO_NOT_CHECKED)


def is_todo_complete(todo):
    """is_todo_complete

    Check if the current todo is complete or not.
    """

    if re.findall(TODO_IS_CHECKED, todo):
        return True
    elif re.findall(TODO_NOT_CHECKED, todo):
        return False

    return False


def make_todo(content):
    """make_todo

    Return a string for the currently incomplete ToDo.
    """

    return f"{BULLET_POINT}   {EMPTY_TODO}: {content}"
