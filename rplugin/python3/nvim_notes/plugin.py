from functools import wraps

import neovim
import os

from nvim_notes.utils.make_markdown_file import produce_daily_markdown


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

    @neovim.autocmd('BufEnter', pattern=FILE_TYPE, sync=True)
    def event_buf_enter(self):
        if self._options is None:
            self._options = PluginOptions(self._nvim)

    @neovim.autocmd('BufNewFile', pattern=FILE_TYPE)
    def on_new_file(self):
        schedule_today = produce_daily_markdown(self._options)
        buffer_number = self._nvim.current.buffer.number
        self._nvim.api.buf_set_lines(buffer_number, 0, -1, True, schedule_today)

    @neovim.command('GenerateSchedule', sync=True)
    # @if_active
    def generate_schedule_markdown(self):

        #TODO: Remove this, since it shouldn't be needed due to the autocmds.
        if self._options is None:
            self._options = PluginOptions(self._nvim)

        schedule_today = produce_daily_markdown(self._options)
        buffer_number = self._nvim.current.buffer.number
        self._nvim.api.buf_set_lines(buffer_number, 0, -1, True, schedule_today)

class PluginOptions:

    _defaults = {
        'active': True,
        'config_path': os.getcwd(),
        'headings': ['Notes', 'Issues', 'ToDo'],
        'use_google_calendar': True,
        'calendar_filter_list': []
    }

    def __init__(self, nvim):
        for key, default_value in PluginOptions._defaults.items():
            value = nvim.vars.get(f"nvim_notes#{key}", default_value)
            nvim.vars[f"nvim_notes#{key}"] = value

            setattr(self, key, value)
