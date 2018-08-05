"""neovim_helpers

Simple helpers to help interfacing with NeoVim.
"""


def is_buffer_empty(nvim):
    """is_buffer_empty

    Checks if the buffer is empty.
    """

    return get_buffer_contents(nvim) == [""]


def get_buffer_contents(nvim):
    """get_buffer_contents

    Get the contents of the current buffer.
    """

    buffer_number = nvim.current.buffer.number

    return nvim.api.buf_get_lines(buffer_number, 0, -1, True)


def set_buffer_contents(nvim, data):
    """set_buffer_contents

    Set the contents of the current buffer.
    """
    buffer_number = nvim.current.buffer.number

    nvim.api.buf_set_lines(buffer_number, 0, -1, True, data)


def get_line_content(nvim, line_offset=None):
    """get_line_content

    Get the contents of the current line.
    """

    buffer_number = nvim.current.buffer.number
    cursor_line = nvim.current.window.cursor[0]

    if line_offset:
        cursor_line += line_offset

    return nvim.api.buf_get_lines(buffer_number, cursor_line - 1, cursor_line, True)[0]


def set_line_content(nvim, data, line_index=None, line_offset=None):
    """set_line_content

    Set the contents of the given buffer lines, or the current line if no
    index is given.
    """
    buffer_number = nvim.current.buffer.number

    if line_index is None:
        line_index = nvim.current.window.cursor[0]

    if line_offset is None:
        line_offset = 0

    nvim.api.buf_set_lines(
        buffer_number, line_index - 1, line_index + line_offset - 1, True, data
    )


def get_section_line(buffer_contents, section_line):
    """get_section_line

    Given a buffer, get the line that the schedule section starts on.
    """

    buffer_section_index = -1

    # Do the search in reverse since we know the schedule comes last
    for line_index, line in enumerate(reversed(buffer_contents)):
        if line == section_line:
            buffer_section_index = line_index

    buffer_section_index = len(buffer_contents) - buffer_section_index

    return buffer_section_index


def buffered_info_message(nvim, message):
    """buffered_info_message

    A helper function to return an info message to the user.
    This is buffered, so this will not print anything until a final
    newline (\n) is sent.
    """

    nvim.out_write(f"{message}")
