import neovim
from utils.make_markdown_file import make_schedule

@neovim.plugin
class NotesPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.autocmd('BufNewFile', pattern='*.md', eval='expand("<afile>")', sync=True)
    def on_new_file(self, filename):
        self.nvim.out_write('testplugin is in ' + filename + '\n')

    @neovim.function('TestFunction', sync=True)
    def testfunction(self, args):
        return 3

    @neovim.command('TestCommand', nargs='*', range='')
    def testcommand(self, args, range):
        self.nvim.current.line = ('Command with args: {}, range: {}'
                                  .format(args, range))
        schedule_today = make_schedule()
        self.nvim.current.buffer.append(schedule_today)

