from typing import List, Tuple


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

        self.set_count = 0
        self.get_count = 0

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
        elif start == end:
            if replacement == []:
                del self.nvim.current.buffer.lines[start]
            else:
                self.nvim.current.buffer.lines[start:end] = replacement
        else:
            self.nvim.current.buffer.lines[start:end] = replacement

        self.set_count += 1

    def buf_get_lines(
        self, buffer: int, start: int, end: int, strict_indexing: bool
    ) -> List[str]:

        self.get_count += 1

        if end == -1:
            return self.nvim.current.buffer.lines[start:]

        return self.nvim.current.buffer.lines[start:end]


class MockNvimCurrent:
    def __init__(self) -> None:
        self.window: MockNvimWindow = MockNvimWindow()
        self.buffer: MockNvimBuffer = MockNvimBuffer()


class MockNvimBuffer:
    def __init__(self) -> None:
        self.number: int = 0
        self.lines: List[str] = [""]
        self.name: str = ""


class MockNvimWindow:
    def __init__(self) -> None:
        self.cursor: Tuple[int, int] = (0, 0)
