
import unittest

from typing import List

from .mocks.nvim import MockNvim
from ..helpers.markdown_helpers import sort_markdown_events


class markdown_helpersTest(unittest.TestCase):
    """
    Tests for functions in the markdown_helpers module.
    """

    def test_sort_markdown_events(self) -> None:

        nvim: MockNvim = MockNvim()
        nvim.current.buffer.lines = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "## Schedule",
            "",
            "- 10:00 - 11:00: Event 2",
            "- 14:00 - 16:00: Event 4",
            "- 14:00 - 15:00: Event 3",
            "- 10:00 - 11:00: Event 1",
            "",
        ]

        final_buffer: List[str] = [
            "<!---",
            "    Date: 2018-01-01",
            "    Tags:",
            "--->",
            "# Diary for 2018-01-01",
            "",
            "## Notes",
            "",
            "## Issues",
            "",
            "## Schedule",
            "",
            "- 10:00 - 11:00: Event 1",
            "- 10:00 - 11:00: Event 2",
            "- 14:00 - 15:00: Event 3",
            "- 14:00 - 16:00: Event 4",
            "",
        ]

        sort_markdown_events(nvim)
        assert nvim.current.buffer.lines == final_buffer

        # Calling when sorted should mean no change.
        nvim.api.get_count = 0
        nvim.api.set_count = 0
        sort_markdown_events(nvim)
        assert nvim.current.buffer.lines == final_buffer
        assert nvim.api.get_count == 1
        assert nvim.api.set_count == 0
