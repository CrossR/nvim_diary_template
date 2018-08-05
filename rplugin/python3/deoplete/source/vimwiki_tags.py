# pylint: disable=all
import glob
import re
from collections import namedtuple
from os import path

from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.__pattern = re.compile(f":[a-zA-Z]*")

        self.name = 'vw_tag'
        self.mark = '[VW]'
        self.filetypes = ['vimwiki']
        self.min_pattern_length = 0
        self.notes_path = self.vim.eval('g:nvim_diary_template#notes_path')

    def gather_candidates(self, context):

        pattern = path.join(
            self.notes_path,
            ".tags"
        )

        tag_list = []

        try:
            tags_file = glob.glob(pattern)[0]

            with open(tags_file, 'r', errors='replace') as f:
                for line in f:
                    if re.match(r'^!', line):
                        continue

                    tag_list.append(line.split('\t')[0])

        except (IndexError, FileNotFoundError):
            pass

        return [{'word': f":{tag}:"} for tag in tag_list]

    def get_complete_position(self, context):
        match = self.__pattern.search(context['input'])
        return match.start() if match is not None else -1
