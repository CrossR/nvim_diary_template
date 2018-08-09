# pylint: disable=all
import neovim
import os

from nvim_diary_template.plugin import DiaryTemplatePlugin

pipes = os.listdir('\\\\.\\pipe')
current_pipe = [pipe for pipe in pipes if pipe.startswith('nvim')][0]
nvim = neovim.attach('socket', path=f"\\\\.\\pipe\\{current_pipe}")
DiaryTemplatePlugin(nvim).make_diary()