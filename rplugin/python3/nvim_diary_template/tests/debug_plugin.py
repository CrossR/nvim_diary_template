# pylint: disable=all
import neovim
import os

from nvim_diary_template.plugin import DiaryTemplatePlugin

# A basic script to start up a neovim instance and start the plugin running.
# This is intended to be used with a debugger, to move through the plugin.
PIPES = os.listdir("\\\\.\\pipe")
CURRENT_PIPE = [pipe for pipe in PIPES if pipe.startswith("nvim")][0]
NVIM = neovim.attach("socket", path=f"\\\\.\\pipe\\{CURRENT_PIPE}")
DiaryTemplatePlugin(NVIM).make_diary()

