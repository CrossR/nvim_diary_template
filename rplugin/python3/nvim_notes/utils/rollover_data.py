from nvim_notes.helpers.file_helpers import (get_note_path,
                                             get_note_file_content,
                                             get_past_notes)
from nvim_notes.utils.constants import TODO_IS_CHECKED, TODO_NOT_CHECKED
from nvim_notes.utils.parse_markdown import parse_markdown_file_for_todos


def get_past_todos(nvim, options):

    past_files = get_past_notes(options)

    for past_file in past_files:
        full_file_path = get_note_path(options, past_file)
        buffer_content = get_note_file_content(full_file_path)
        todos = parse_markdown_file_for_todos(current_buffer=buffer_content)

        uncompleted_todos = [todo for todo in todos if todo['completed'] == False]

        # For the uncompleted, add to array.
        # Add schedule like function to make lines of ToDos.
        # Call and add to buffer.
        # Add to creation of file.
