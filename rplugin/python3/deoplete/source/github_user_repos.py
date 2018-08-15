# pylint: disable=all
import glob
import json
import re
from collections import namedtuple
from os import path

from .base import Base

LENGTH_OF_PATTERN = 1


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.__pattern = re.compile(f"@")

        self.name = "gh_repo"
        self.mark = "[GHR]"
        self.filetypes = ["vimwiki"]
        self.min_pattern_length = 0
        self.rank = 550
        self.config_folder = self.vim.eval("g:nvim_diary_template#config_path")
        self.user_name = self.vim.eval("g:nvim_diary_template#user_name")

    def gather_candidates(self, context):

        if self.user_name == "":
            return []

        cache_path = path.join(self.config_folder, "cache")

        pattern = path.join(cache_path, f"nvim_diary_template_user_repos_cache_*.json")

        repos = []

        try:
            repo_file_cache = glob.glob(pattern)[0]

            with open(repo_file_cache, "r", errors="replace") as f:
                repos = json.load(f)

        except (IndexError, FileNotFoundError):
            pass

        repos.insert(0, self.user_name)

        return [{"word": f"@{r}"} for r in repos]

    def get_complete_position(self, context):
        match_pos = context["position"][2] - LENGTH_OF_PATTERN - 1

        if match_pos < 0:
            match_pos = 0

        match = self.__pattern.search(context["input"], match_pos)
        return match.start() if match is not None else -1
