from functools import wraps

import neovim

from nvim_notes.utils.google_cal_integration import SimpleNvimGoogleCal
from nvim_notes.utils.helpers import get_line_content, set_line_content
from nvim_notes.utils.keybind_actions import strikeout_line
from nvim_notes.utils.make_markdown_file import (open_markdown_file,
                                                 parse_markdown_file_for_events,
                                                 sort_markdown_events)
from nvim_notes.utils.plugin_options import PluginOptions

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

    @neovim.command('OpenSchedule')
    # @if_active
    def open_schedule(self):

        # TODO: Remove this, since it shouldn't be needed due to the autocmds.
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )

        open_markdown_file(
            self._nvim,
            self._options,
            self._gcal_service
        )

    @neovim.command('UploadCalendar')
    def upload_to_calendar(self):
        markdown_events = parse_markdown_file_for_events(self._nvim)
        self._gcal_service.upload_to_calendar(markdown_events)

    @neovim.command('SortCalendar')
    def sort_calendar(self):
        sort_markdown_events(self._nvim)

    @neovim.command('StrikeoutLine')
    def strikeout(self):
        current_line = get_line_content(self._nvim)
        set_line_content(self._nvim, strikeout_line(current_line))
