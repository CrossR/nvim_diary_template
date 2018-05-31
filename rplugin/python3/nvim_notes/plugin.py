import os
from functools import wraps
from pathlib import Path

import neovim

from nvim_notes.utils.google_cal_integration import SimpleNvimGoogleCal
from nvim_notes.utils.keybind_actions import strikeout_line
from nvim_notes.utils.make_markdown_file import (make_markdown_file,
                                                 parse_markdown_file_for_events)

FILE_TYPE = '*.md'


def if_active(function):
    """if_active

    A decorator for a function, such that it is only run when
    nvim_notes is ready.

    Taken from numirias/semshi
    """
    @wraps(function)
    def wrapper(self):
        if not self.options.active:
            return
        function(self)
    return wrapper


@neovim.plugin
class NotesPlugin(object):

    def __init__(self, nvim):
        self._nvim = nvim
        self._options = None
        self._gcal_service = None

    @neovim.autocmd('BufEnter', pattern=FILE_TYPE, sync=True)
    def event_buf_enter(self):
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )

    @neovim.autocmd('BufNewFile', pattern=FILE_TYPE)
    def on_new_file(self):
        make_markdown_file(
            self._nvim,
            self._options,
            self._gcal_service
        )

    @neovim.command('GenerateSchedule')
    # @if_active
    def generate_schedule_markdown(self):

        # TODO: Remove this, since it shouldn't be needed due to the autocmds.
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )

        make_markdown_file(
            self._nvim,
            self._options,
            self._gcal_service
        )

    @neovim.command('UpdateCalendar')
    def update_calendar(self):
        markdown_events = parse_markdown_file_for_events(self._nvim)
        self._gcal_service.update_calendar(markdown_events)

        return

    @neovim.command('StrikeoutLine')
    def strikeout(self):
        current_line = self._nvim.api.buf_get_lines(
            self._nvim.current.buffer.number,
            self._nvim.current.window.cursor[0] - 1,
            self._nvim.current.window.cursor[0],
            True
        )

        self._nvim.api.buf_set_lines(
            self._nvim.current.buffer.number,
            self._nvim.current.window.cursor[0] - 1,
            self._nvim.current.window.cursor[0],
            True,
            strikeout_line(current_line[0])
        )


class PluginOptions:

    _defaults = {
        'active': True,
        'config_path': os.getcwd(),
        'notes_path': str(Path.home()),
        'open_method': 'tabnew',
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
