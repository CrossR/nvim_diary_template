# pylint: disable=all
# A basic script to start up a neovim instance and start the plugin running.
# This is intended to be used with a debugger, to move through the plugin.
import pynvim
import os
from typing import List

from nvim_diary_template.plugin import DiaryTemplatePlugin

# Get the current nvim instance. If there are multiple instances, it may be
# more reliable to setup a dedicated address, see:
# http://pynvim.readthedocs.io/en/latest/development.html#usage-through-the-python-repl
PIPES: List[str] = os.listdir("\\\\.\\pipe")
CURRENT_PIPE: str = [pipe for pipe in PIPES if pipe.startswith("nvim")][0]
NVIM: pynvim.Nvim = neovim.attach("socket", path=f"\\\\.\\pipe\\{CURRENT_PIPE}")

# Initialise the options, then run the required function.
plugin: DiaryTemplatePlugin = DiaryTemplatePlugin(NVIM)

plugin.check_options()
plugin.make_diary_command()
