import re

from nvim_notes.utils.constants import (BULLET_POINT, TODO_IS_CHECKED,
                                        TODO_NOT_CHECKED)


def is_todo_complete(todo):
    """is_todo_complete

    Check if the current todo is complete or not.
    """

    if len(re.findall(TODO_IS_CHECKED, todo)) != 0:
        return True
    elif len(re.findall(TODO_NOT_CHECKED, todo)) != 0:
        return False
    else:
        return False


def make_todo(content):
    """make_todo

    Return a string for the currently incomplete ToDo.
    """

    return f"{BULLET_POINT}   {TODO_NOT_CHECKED}: {content}"
