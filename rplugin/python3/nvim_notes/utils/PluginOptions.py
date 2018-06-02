import os
from pathlib import Path

class PluginOptions:

    _defaults = {
        'active': True,
        'config_path': os.getcwd(),
        'notes_path': os.path.join(str(Path.home()), "nvim_notes"),
        'open_method': None,
        'headings': ['Notes', 'Issues', 'ToDo'],
        'use_google_calendar': True,
        'calendar_filter_list': [],
        'add_to_google_cal': False,
        'google_cal_name': 'primary',
        'timezone': 'Europe/London'
    }

    def __init__(self, nvim):
        for key, default_value in PluginOptions._defaults.items():
            value = nvim.vars.get(f"nvim_notes#{key}", default_value)
            nvim.vars[f"nvim_notes#{key}"] = value

            setattr(self, key, value)