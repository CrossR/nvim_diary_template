# pylint: disable=too-few-public-methods, R0902
"""plugin_options

Store the plugin options for the nvim_diary_template class, as
well as any associated helpers.
"""

import os
from pathlib import Path
from typing import List


class PluginOptions:
    """PluginOptions

    Plugin options is a class that stores all the options
    that the nvim_diary_template plugin uses.

    The values are set to some default, and then overridden if any
    value exists in the users' config.
    """

    _defaults = {
        "active": True,
        "notes_path": os.path.join(str(Path.home()), "vimwiki"),
        "config_path": os.path.join(str(Path.home()), "vimwiki", "config"),
        "daily_headings": ["Notes"],
        "use_google_calendar": True,
        "calendar_filter_list": [],
        "add_to_google_cal": False,
        "google_cal_name": "primary",
        "timezone": "Europe/London",
        "use_github_repo": True,
        "repo_name": "",
    }

    def __init__(self, nvim):

        self.active: bool = True
        self.notes_path: str = os.path.join(str(Path.home()), "vimwiki")
        self.config_path: str = os.path.join(str(Path.home()), "vimwiki", "config")
        self.daily_headings: List[str] = ["Notes"]
        self.use_google_calendar: bool = True
        self.calendar_filter_list: List[str] = []
        self.add_to_google_cal: bool = False
        self.google_cal_name: str = "primary"
        self.timezone: str = "Europe/London"
        self.use_github_repo: bool = True
        self.repo_name: str = ""

        for key, default_value in PluginOptions._defaults.items():
            value = nvim.vars.get(f"nvim_diary_template#{key}", default_value)
            nvim.vars[f"nvim_diary_template#{key}"] = value

            setattr(self, key, value)
