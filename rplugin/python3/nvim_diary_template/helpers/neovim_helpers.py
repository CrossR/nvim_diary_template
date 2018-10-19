"""neovim_helpers

Simple helpers to help interfacing with NeoVim.
"""

from os import path
from typing import List

from neovim import Nvim


def is_buffer_empty(nvim: Nvim) -> bool:
    """is_buffer_empty

    Checks if the buffer is empty.
    """

    return get_buffer_contents(nvim) == [""]


def get_buffer_contents(nvim: Nvim) -> List[str]:
    """get_buffer_contents

    Get the contents of the current buffer.
    """

    buffer_number: int = nvim.current.buffer.number

    buffer_contents: List[str] = nvim.api.buf_get_lines(buffer_number, 0, -1, True)

    return buffer_contents


def set_buffer_contents(nvim: Nvim, data: List[str]) -> None:
    """set_buffer_contents

    Set the contents of the current buffer.
    """
    buffer_number: int = nvim.current.buffer.number

    nvim.api.buf_set_lines(buffer_number, 0, -1, True, data)


def set_line_content(
    nvim: Nvim, data: List[str], line_index: int = -1, line_offset: int = -1
) -> None:
    """set_line_content

    Set the contents of the given buffer lines, or the current line if no
    index is given.
    """
    buffer_number: int = nvim.current.buffer.number

    if line_index == -1:
        line_index = nvim.current.window.cursor[0]

    if line_offset == -1:
        line_offset = 0

    nvim.api.buf_set_lines(
        buffer_number, line_index - 1, line_index + line_offset - 1, True, data
    )


def get_section_line(buffer_contents: List[str], section_line: str) -> int:
    """get_section_line

    Given a buffer, get the line that the schedule section starts on.
    """

    section_index: int = -1

    # Do the search in reverse since we know the schedule comes last
    for line_index, line in enumerate(reversed(buffer_contents)):
        if line == section_line:
            section_index = line_index

    final_index: int = len(buffer_contents) - section_index

    return final_index


def buffered_info_message(nvim: Nvim, message: str) -> None:
    """buffered_info_message

    A helper function to return an info message to the user.
    This is buffered, so this will not print anything until a final
    newline (\n) is sent.
    """

    nvim.out_write(f"{message}")


def get_diary_date(nvim: Nvim) -> str:
    """get_diary_date

    Get the date of the current diary file.
    This is just the filename, without the extension.
    """

    if "diary" not in nvim.current.buffer.name:
        return ""

    file_name: str = path.basename(nvim.current.buffer.name)
    return path.splitext(file_name)[0]
