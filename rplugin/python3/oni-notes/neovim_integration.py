import neovim

@neovim.plugin
class NotesPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.autocmd('BufNewFile', pattern='*.md', eval='expand("<afile>")', sync=True)
    def on_new_file(self, filename):
        self.nvim.out_write('testplugin is in ' + filename + '\n')

