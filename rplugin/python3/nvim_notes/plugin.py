from functools import wraps

import neovim

from nvim_notes.utils.make_markdown_file import produce_daily_markdown


def if_active(function):
    """if_active

    A decorator for a function, such that it is only run when
    nvim-notes is ready.

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
        self.nvim = nvim
        self.options = None

    @neovim.autocmd('BufNewFile', pattern='*.md')
    def on_new_file(self):
        schedule_today = produce_daily_markdown(self.options)
        buffer_number = self.nvim.buffer.number
        self.nvim.api.buf_set_lines(buffer_number, 0, -1, True, schedule_today)

    @neovim.command('GenerateSchedule')
    @if_active
    def testcommand(self):
        schedule_today = produce_daily_markdown(self.options)
        self.nvim.current.buffer.append(schedule_today)

class PluginOptions:

    _defaults = {
        'active': True,
        'credentials_path': ''
    }
