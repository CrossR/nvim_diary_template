
import json
import os
import shutil
import tempfile
import time as t
import unittest
from datetime import timedelta
from random import choices
from typing import Any, Dict, List

from ..helpers.file_helpers import check_cache, generate_diary_index, set_cache
from .mocks.options import MockPluginOptions


class file_helpersTest(unittest.TestCase):
    """
    Tests for functions in the file_helpers module.
    """

    def setUp(self) -> None:
        self.options = MockPluginOptions()
        self.config = tempfile.mkdtemp()
        self.options.config_path = self.config

    def tearDown(self) -> None:
        shutil.rmtree(self.config)

    def test_check_cache(self) -> None:
        os.makedirs(os.path.join(self.config, "cache"))
        random_string: List[str] = choices("abcdefghijklmnop", k=4)

        def fallback() -> Dict[Any, Any]:
            return {"Issues": ["Two", "Four", "Six", random_string]}

        # Make a cache file and check it loads.
        with open(
            os.path.join(
                self.config,
                "cache",
                f"nvim_diary_template_test_cache_{int(t.time())}.json",
            ),
            "w",
        ) as json_file:
            json.dump({"Issues": ["One", "Three", "Five"]}, json_file)

        result = check_cache(self.config, "test", timedelta(days=1), fallback)
        assert result == {"Issues": ["One", "Three", "Five"]}

        # Now test that an old cache file is ignored.
        # Done by setting a tiny timedelta.
        result = check_cache(self.config, "test", timedelta(microseconds=1), fallback)
        assert result == {"Issues": ["Two", "Four", "Six", random_string]}

        # Test the existing file is still there.
        result = check_cache(self.config, "test", timedelta(days=1), fallback)
        assert result == {"Issues": ["Two", "Four", "Six", random_string]}
