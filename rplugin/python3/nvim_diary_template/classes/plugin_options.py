# pylint: disable=too-few-public-methods, R0902
"""plugin_options

Store the plugin options for the nvim_diary_template class, as
well as any associated helpers.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from neovim import Nvim

from ..utils.constants import DEFAULT_SORT_ORDER


class PluginOptions:
    """PluginOptions

    Plugin options is a class that stores all the options
    that the nvim_diary_template plugin uses.

    The values are set to some default, and then overridden if any
    value exists in the users' config.
    """

    def __init__(self, nvim: Optional[Nvim] = None) -> None:

        self.active: bool = True
        self.notes_path: str = os.path.join(str(Path.home()), "wiki")
        self.config_path: str = os.path.join(str(Path.home()), "wiki", "config")
        self.daily_headings: List[str] = ["Notes"]
        self.auto_generate_diary_index = False
        self.use_google_calendar: bool = True
        self.calendar_filter_list: List[str] = []
        self.issue_groups: List[str] = []
        self.add_to_google_cal: bool = False
        self.google_cal_name: str = "primary"
        self.timezone: str = "Europe/London"
        self.use_github_repo: bool = True
        self.repo_name: str = ""
        self.user_name: str = ""
        self.sort_issues_on_upload: bool = False
        self.sort_order: Dict[str, int] = DEFAULT_SORT_ORDER

        if nvim is not None:
            for key, default_value in self.__dict__.items():
                value: Any = nvim.vars.get(f"nvim_diary_template#{key}", default_value)
                nvim.vars[f"nvim_diary_template#{key}"] = value

                setattr(self, key, value)
