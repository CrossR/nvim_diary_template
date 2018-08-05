# pylint: disable=all
import glob
import json
import re
from collections import namedtuple
from os import path

from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.__pattern = re.compile(f"\+label:")

        self.name = 'gh_label'
        self.mark = '[GH]'
        self.filetypes = ['vimwiki']
        self.min_pattern_length = 0
        self.config_folder = self.vim.eval('g:nvim_diary_template#config_path')

    def gather_candidates(self, context):

        cache_path = path.join(
            self.config_folder,
            "cache",
        )

        pattern = path.join(
            cache_path,
            f"nvim_diary_template_repo_labels_cache_*.json"
        )

        try:
            label_file_cache = glob.glob(pattern)[0]

            with open(label_file_cache, 'r', errors='replace') as f:
                label_list = json.load(f)

        except (IndexError, FileNotFoundError):
            label_list = []

        return [{'word': f"+label:{l}"} for l in label_list]

    def get_complete_position(self, context):
        match = self.__pattern.search(context['input'])
        return match.start() if match is not None else -1
