
import unittest

from typing import List

from .mocks.nvim import mock_nvim
from rplugin.python3.nvim_diary_template.helpers.neovim_helpers import is_buffer_empty, get_buffer_contents


class neovim_helpersTest(unittest.TestCase):
    """
    Tests for functions in the neovim_helpers module.
    """

    def setUp(self) -> None:
        self.nvim: mock_nvim = mock_nvim()

    def tearDown(self) -> None:
        pass  # TODO

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
        raise NotImplementedError()  # TODO: test set_buffer_contents

    def test_get_line_content(self) -> None:
        raise NotImplementedError()  # TODO: test get_line_content

    def test_set_line_content(self) -> None:
        raise NotImplementedError()  # TODO: test set_line_content

    def test_get_section_line(self) -> None:
        raise NotImplementedError()  # TODO: test get_section_line

    def test_buffered_info_message(self) -> None:
        raise NotImplementedError()  # TODO: test buffered_info_message
