# pylint: disable=all
import neovim
import os
from typing import List

from nvim_diary_template.plugin import DiaryTemplatePlugin

# A basic script to start up a neovim instance and start the plugin running.
# This is intended to be used with a debugger, to move through the plugin.
PIPES: List[str] = os.listdir("\\\\.\\pipe")
CURRENT_PIPE: str = [pipe for pipe in PIPES if pipe.startswith("nvim")][0]
NVIM: neovim.Nvim = neovim.attach("socket", path=f"\\\\.\\pipe\\{CURRENT_PIPE}")

DiaryTemplatePlugin(NVIM).grab_from_calendar()
