
import unittest
from unittest.mock import MagicMock, create_autospec

from .mocks.nvim import MockNvim
from ..helpers.issue_helpers import insert_edit_tag


class issue_helpersTest(unittest.TestCase):
    """
    Tests for functions in the issue_helpers module.
    """

    def setUp(self) -> None:
        self.nvim = MockNvim()

    def tearDown(self) -> None:
        pass  # TODO

    def test_insert_edit_tag(self) -> None:
        raise NotImplementedError()

    def test_insert_new_issue(self) -> None:
        raise NotImplementedError()  # TODO: test insert_new_issue

    def test_insert_new_comment(self) -> None:
        raise NotImplementedError()  # TODO: test insert_new_comment

    def test_toggle_issue_completion(self) -> None:
        raise NotImplementedError()  # TODO: test toggle_issue_completion

    def test_check_markdown_style(self) -> None:
        raise NotImplementedError()  # TODO: test check_markdown_style

    def test_vimwiki_to_github_process(self) -> None:
        raise NotImplementedError()  # TODO: test vimwiki_to_github_process

    def test_github_to_vimwiki_process(self) -> None:
        raise NotImplementedError()  # TODO: test github_to_vimwiki_process

    def test_convert_utc_timezone(self) -> None:
        raise NotImplementedError()  # TODO: test convert_utc_timezone

    def test_sort_issues(self) -> None:
        raise NotImplementedError()  # TODO: test sort_issues

    def test_sort_completion_state(self) -> None:
        raise NotImplementedError()  # TODO: test sort_completion_state

    def test_get_github_objects(self) -> None:
        raise NotImplementedError()  # TODO: test get_github_objects

    def test_split_comment(self) -> None:
        raise NotImplementedError()  # TODO: test split_comment

    def test_get_issue_index(self) -> None:
        raise NotImplementedError()  # TODO: test get_issue_index
