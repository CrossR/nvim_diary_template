import re

from nvim_notes.utils.constants import TODO_IS_CHECKED, TODO_NOT_CHECKED


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
