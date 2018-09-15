
from typing import List


class MockNvim:
    def __init__(self) -> None:
        self.api: MockNvimApi = MockNvimApi(self)
        self.current: MockNvimCurrent = MockNvimCurrent()
        self.commands: List[str] = []
        self.errors: List[str] = []
        self.messages: List[str] = []

        self.error_print_count = 0
        self.message_print_count = 0

    def err_write(self, message: str) -> None:
        if message.endswith("\n"):
            self.message_print_count += 1

        self.errors.append(message)

    def out_write(self, message: str) -> None:
        if message.endswith("\n"):
            self.message_print_count += 1

        self.messages.append(message)
    
    def command(self, command: str) -> None:
        self.commands.append(command)


class MockNvimApi:
    def __init__(self, nvim_mock: MockNvim) -> None:
        self.nvim: MockNvim = nvim_mock

    def buf_set_lines(
        self,
        buffer: int,
        start: int,
        end: int,
        strict_indexing: bool,
        replacement: List[str],
    ) -> None:

        if end == -1:
            self.nvim.current.buffer.lines[start:] = replacement
        else:
            self.nvim.current.buffer.lines[start : end + 1] = replacement

    def buf_get_lines(
        self, buffer: int, start: int, end: int, strict_indexing: bool
    ) -> List[str]:

        if end == -1:
            return self.nvim.current.buffer.lines[start:]
        else:
            return self.nvim.current.buffer.lines[start:end]


class MockNvimCurrent:
    def __init__(self) -> None:
        self.window: MockNvimWindow = MockNvimWindow()
        self.buffer: MockNvimBuffer = MockNvimBuffer()


class MockNvimBuffer:
    def __init__(self) -> None:
        self.number: int = 0
        self.lines: List[str] = [""]


class MockNvimWindow:
    def __init__(self) -> None:
        self.cursor: tuple = tuple()
