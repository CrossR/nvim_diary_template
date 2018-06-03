import json
import re

from nvim_notes.helpers.file_helpers import (get_note_file_content,
                                             get_note_path, get_past_notes)
from nvim_notes.helpers.neovim_helpers import (get_buffer_contents,
                                               get_section_line)
from nvim_notes.helpers.todo_helpers import is_todo_complete, make_todo
from nvim_notes.utils.constants import (SCHEDULE_HEADING, TODO_HEADING,
                                        TODO_ONGOING_REGEX, TODO_REGEX)


def get_past_todos(nvim, options):

    past_files = get_past_notes(options)

    todo_markdown = [TODO_HEADING,""]

    for past_file in past_files:
        full_file_path = get_note_path(options, past_file)
        buffer_content = get_note_file_content(full_file_path)
        todos = parse_markdown_file_for_todos(current_buffer=buffer_content)

        uncompleted_todos = [
            todo for todo in todos if todo['completed'] == False]

        for todo in uncompleted_todos:
            todo_markdown.append(make_todo(todo))

    with open("F:\\old_todos.json", 'w') as old:
        json.dump(todos, old)

    return todo_markdown

        # Call and add to buffer.
        # Add to creation of file.


def parse_markdown_file_for_todos(nvim=None, current_buffer=None):
    """parse_markdown_file_for_todos

    Gets the contents of the current NeoVim buffer,
    and parses the todo section.
    """

    if current_buffer == None and nvim is not None:
        current_buffer = get_buffer_contents(nvim)

    todo_start = get_section_line(current_buffer, TODO_HEADING)
    todo_end = get_section_line(current_buffer, SCHEDULE_HEADING) - 1
    todos = current_buffer[todo_start:todo_end]
    formatted_todos = parse_buffer_todos(todos)

    return formatted_todos


def parse_buffer_todos(todos):
    """parse_buffer_todos

    Given a list of ToDos, parse the buffer lines and format to ToDos.
    """

    formatted_todos = []

    for todo in todos:
        if todo == '':
            continue

        # TODO: Regex is probably going to be a giant pain here,
        # and won't work if the string pattern changes.
        todo_started = re.findall(TODO_REGEX, todo)
        todo_carrying_on = re.findall(TODO_ONGOING_REGEX, todo)

        if len(todo_started) > 0:
            formatted_todos.append({
                'todo': todo_started[0],
                'complete': is_todo_complete(todo)
            })
        elif len(todo_carrying_on) > 0:
            full_todo = f"{formatted_todos[-1]} {todo_carrying_on[0]}"
            formatted_todos[-1]['todo'] = full_todo

    return formatted_todos
