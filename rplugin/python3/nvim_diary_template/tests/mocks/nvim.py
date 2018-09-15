
from typing import List


class mock_nvim:
    def __init__(self) -> None:
        self.api: mock_nvim_api = mock_nvim_api(self)
        self.current: mock_current = mock_current()
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


class mock_nvim_api:
    def __init__(self, nvim_mock: mock_nvim) -> None:
        self.nvim: mock_nvim = nvim_mock

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
            self.nvim.current.buffer.lines[start:end + 1] = replacement

    def buf_get_lines(
        self, buffer: int, start: int, end: int, strict_indexing: bool
    ) -> List[str]:

        if end == -1:
            return self.nvim.current.buffer.lines[start:]
        else:
            return self.nvim.current.buffer.lines[start:end]


class mock_current:
    def __init__(self) -> None:
        self.window: mock_window = mock_window()
        self.buffer: mock_buffer = mock_buffer()


class mock_buffer:
    def __init__(self) -> None:
        self.number: int = 0
        self.lines: List[str] = [""]


class mock_window:
    def __init__(self) -> None:
        self.cursor: tuple = tuple()
