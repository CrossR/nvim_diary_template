import neovim
from nvim_notes.utils import make_markdown_file

@neovim.plugin
class NotesPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.autocmd('BufNewFile', pattern='*.md')
    def on_new_file(self):
        schedule_today = make_markdown_file.produce_daily_schedule()
        self.nvim.current.buffer.append(schedule_today)

    @neovim.function('TestFunction', sync=True)
    def testfunction(self, args):
        return 3

    @neovim.command('GenerateSchedule')
    def testcommand(self):
        schedule_today = make_markdown_file.produce_daily_schedule()
        self.nvim.current.buffer.append(schedule_today)

