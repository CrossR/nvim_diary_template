"""neovim_helpers

Simple helpers to help interfacing with NeoVim.
"""

import re

from nvim_notes.utils.constants import BULLET_POINT_REGEX


def open_file(nvim, file_path, open_method=None):
    """open_file

    Attempts to open the given file in the specified way. If no method is
    given, open in the current buffer if it is empty and not modified, and in
    a new tab if not.
    """

    if open_method is None:
        if not buf_is_modified(nvim) and \
           not buf_file_open(nvim):
            nvim.command(f":e {file_path}")
        else:
            nvim.command(f":tabnew {file_path}")
    else:
        nvim.command(f":{open_method} {file_path}")


def open_popup_file(nvim, file_path, open_method=None):
    """open_popup_file

    Opens the given file in a small pop-out split. That is depending on the
    user config, open a small split on the bottom or side of the current
    window.

    The default open method is `botright 15split`, ie a split 15 lines tall
    on the bottom right. `80vs` would achieve a vertical split of 80 columns.
    `:help opening-window` for more examples.

    Returns the new splits buffer number for later usage.
    """

    if open_method is None:
        open_method = "botright 15split"

    nvim.command(f":{open_method} {file_path}")

    return nvim.current.buffer.number


def buf_is_modified(nvim):
    """buf_is_modified

    Return true if the buffer is modified.
    """

    return int(nvim.command_output('echo &modified'))


def get_current_word(nvim):
    """get_current_word

    Get the word the cursor is currently over.
    """

    return str(nvim.command_output('echo(expand("<cword>"))'))


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


def get_line_content(nvim, line_offset=None):
    """get_line_content

    Get the contents of the current line.
    """

    buffer_number = nvim.current.buffer.number
    cursor_line = nvim.current.window.cursor[0]

    if line_offset:
        cursor_line += line_offset

    return nvim.api.buf_get_lines(
        buffer_number,
        cursor_line - 1,
        cursor_line,
        True
    )[0]


def get_multi_line_bullet(nvim):
    """get_multi_line_bullet

    Gets the entire instance of a line.
    That is, for a multi-line bullet point, get every part of the line.
    """

    current_lines = [get_line_content(nvim)]

    line_offset = 1
    next_line = get_line_content(nvim, line_offset)

    # Keep getting the lines beneath until the next bullet point is found, Or
    # the line is empty.
    while next_line and not re.findall(BULLET_POINT_REGEX, next_line):
        line_offset += 1

        current_lines.append(next_line)
        next_line = get_line_content(nvim, line_offset)

    return current_lines


def set_line_content(
        nvim,
        data,
        line_index=None,
        line_offset=None):
    """set_line_content

    Set the contents of the current line.
    """
    buffer_number = nvim.current.buffer.number

    if line_index is None:
        line_index = nvim.current.window.cursor[0]

    if line_offset is None:
        line_offset = 0

    nvim.api.buf_set_lines(
        buffer_number,
        line_index - 1,
        line_index + line_offset - 1,
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
