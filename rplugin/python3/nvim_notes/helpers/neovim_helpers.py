
def open_file(nvim, path, open_method):
    """open_file

    Opens the file in the specified way.
    """

    nvim.command(f":{open_method} {path}")


def get_buffer_contents(nvim):
    """get_buffer_contents

    Get the contents of the current buffer.
    """

    buffer_number = nvim.current.buffer.number

    return nvim.api.buf_get_lines(
        buffer_number,
        0,
        -1,
        True
    )


def set_buffer_contents(nvim, data):
    """set_buffer_contents

    Set the contents of the current buffer.
    """
    buffer_number = nvim.current.buffer.number

    nvim.api.buf_set_lines(
        buffer_number,
        0,
        -1,
        True,
        data
    )


def get_line_content(nvim):
    """get_line_content

    Get the contents of the current line.
    """

    buffer_number = nvim.current.buffer.number
    cursor_line = nvim.current.window.cursor[0]

    return nvim.api.buf_get_lines(
        buffer_number,
        cursor_line - 1,
        cursor_line,
        True
    )[0]


def set_line_content(
        nvim,
        data,
        line_index=None):
    """set_line_content

    Set the contents of the current line.
    """
    buffer_number = nvim.current.buffer.number

    if line_index == None:
        line_index = nvim.current.window.cursor[0]

    nvim.api.buf_set_lines(
        buffer_number,
        line_index - 1,
        line_index,
        True,
        data
    )
