import unittest
from typing import List

from ..helpers.neovim_helpers import (
    buffered_info_message,
    get_buffer_contents,
    get_section_line,
    is_buffer_empty,
    set_buffer_contents,
    set_line_content,
)
from ..utils.constants import ISSUE_HEADING, SCHEDULE_HEADING
from .mocks.mock_nvim import MockNvim


class neovim_helpersTest(unittest.TestCase):
    """
    Tests for functions in the neovim_helpers module.
    """

    def setUp(self) -> None:
        self.nvim: MockNvim = MockNvim()

    def test_is_buffer_empty(self) -> None:
        # The buffer is initialised to be empty, so should be empty straight
        # away.
        result: bool = is_buffer_empty(self.nvim)
        assert result == True

        self.nvim.current.buffer.lines = ["Line added!"]
        result = is_buffer_empty(self.nvim)
        assert result == False

    def test_get_buffer_contents(self) -> None:
        # The buffer is initialised to be empty, so should be empty straight
        # away.
        result: List[str] = get_buffer_contents(self.nvim)
        assert result == [""]

        self.nvim.current.buffer.lines = ["Line added!"]
        result = get_buffer_contents(self.nvim)
        assert result == ["Line added!"]

    def test_set_buffer_contents(self) -> None:
        # First ensure the buffer is empty, then set it.
        assert self.nvim.current.buffer.lines == [""]

        set_buffer_contents(self.nvim, ["This is a new line", "And a second one."])
        assert self.nvim.current.buffer.lines == [
            "This is a new line",
            "And a second one.",
        ]

    def test_set_line_content(self) -> None:
        self.nvim.current.buffer.lines = [
            "<!---",
            "    Date: 2018-09-14",
            "    Tags:",
            "--->",
            "# Diary for 2018-09-15",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "## Schedule",
            "",
        ]
        self.nvim.current.window.cursor = (5, 0)

        # First test removing a line.
        set_line_content(self.nvim, [])
        assert len(self.nvim.current.buffer.lines) == 11

        # Then setting one.
        set_line_content(self.nvim, ["# Diary for 2018-09-15"])
        assert self.nvim.current.buffer.lines[4] == "# Diary for 2018-09-15"

        # Then one not at the cursor position
        set_line_content(self.nvim, ["    Date: 2018-09-15"], 2)
        assert self.nvim.current.buffer.lines[1] == "    Date: 2018-09-15"

        # Finally a range.
        set_line_content(self.nvim, ["", "Note:", "Add unit tests."], 8, 3)
        assert self.nvim.current.buffer.lines[7:10] == ["", "Note:", "Add unit tests."]

    def test_get_section_line(self) -> None:
        self.nvim.current.buffer.lines = [
            "<!---",
            "    Date: 2018-09-15",
            "    Tags:",
            "--->",
            "# Diary for 2018-09-15",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "## Schedule",
            "",
        ]

        result: int = get_section_line(self.nvim.current.buffer.lines, ISSUE_HEADING)
        assert result == 9

        result = get_section_line(self.nvim.current.buffer.lines, SCHEDULE_HEADING)
        assert result == 11

    def test_buffered_info_message(self) -> None:
        assert self.nvim.messages == []

        buffered_info_message(self.nvim, "Info message to send...")

        assert self.nvim.messages == ["Info message to send..."]
        assert self.nvim.message_print_count == 0

        buffered_info_message(self.nvim, "Second one to send.\n")

        assert self.nvim.messages == [
            "Info message to send...",
            "Second one to send.\n",
        ]
        assert self.nvim.message_print_count == 1
