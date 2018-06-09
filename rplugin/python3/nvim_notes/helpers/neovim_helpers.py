"""neovim_helpers

Simple helpers to help interfacing with NeoVim.
"""

from os import path

def open_file(nvim, file_path, open_method=None, force_open=False):
    """open_file

    Attempts to open the given file in the specified way. First checks the
    file exists if required, and if it does opens the file in the requested
    way. Otherwise, open in the current buffer if it is empty and not
    modified, and in a new tab if not.
    """

    if not path.isfile(file_path) and not force_open:
        return False

    if open_method is None:
        if not buf_is_modified(nvim) and \
           not buf_file_open(nvim):
            nvim.command(f":e {file_path}")
        else:
            nvim.command(f":tabnew {file_path}")
    else:
        nvim.command(f":{open_method} {file_path}")

    return True


def buf_is_modified(nvim):
    """buf_is_modified

    Return true if the buffer is modified.
    """

    return int(nvim.command_output('echo &modified'))


def buf_file_open(nvim):
    """buf_file_open

    Return true if a file is open in the current buffer.
    """

    return nvim.current.buffer.name != ''


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

    if line_index is None:
        line_index = nvim.current.window.cursor[0]

    nvim.api.buf_set_lines(
        buffer_number,
        line_index - 1,
        line_index,
        True,
        data
    )


def get_section_line(buffer_contents, section_line):
    """get_section_line

    Given a buffer, get the line that the schedule section starts on.
    """

    buffer_events_index = -1

    # Do the search in reverse since we know the schedule comes last
    for line_index, line in enumerate(reversed(buffer_contents)):
        if line == section_line:
            buffer_events_index = line_index

    buffer_events_index = len(buffer_contents) - buffer_events_index

    return buffer_events_index
