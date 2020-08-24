from pynvim import Nvim
from pynvim.api.window import Window
from pynvim.api.buffer import Buffer
from pynvim.api.tabpage import Tabpage
from enum import Enum
from asyncio import Future
from os import linesep
from typing import Any, Awaitable, Callable, TypeVar, Sequence, Tuple, Iterator, Optional

T = TypeVar("T")


class WindowLayout(Enum):
    LEFT = 1
    BELOW = 2


def init_nvim(nvim: Nvim) -> None:
    global _nvim
    _nvim = nvim


def call_nvim(func: Callable[[], T]) -> Awaitable[T]:
    future: Future = Future()

    def run() -> None:
        try:
            ret = func()
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result(ret)

    _nvim.async_call(run)
    return future


def get_current_buffer_name() -> str:
    buffer = _nvim.api.get_current_buf()
    buffer_name = _nvim.api.buf_get_name(buffer)

    return buffer_name


def get_current_win() -> Window:
    return _nvim.api.get_current_win()


def create_buffer(file_type: str) -> Buffer:
    options = {"noremap": True, "silent": True, "nowait": True}
    buffer: Buffer = _nvim.api.create_buf(False, True)
    _nvim.api.buf_set_option(buffer, "modifiable", False)
    _nvim.api.buf_set_option(buffer, "filetype", file_type)

    return buffer


def find_windows_in_tab() -> Iterator[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = _nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = _nvim.api.get_current_tabpage()
    windows: Sequence[Window] = _nvim.api.tabpage_list_wins(tab)

    for window in sorted(windows, key=key_by):
        if not _nvim.api.win_get_option(window, "previewwindow"):
            yield window


def create_window(size: int, layout: WindowLayout) -> Window:
    split_right = _nvim.api.get_option("splitright")
    split_below = _nvim.api.get_option("splitbelow")

    windows: Sequence[Window] = tuple(window
                                      for window in find_windows_in_tab())

    focus_win = windows[0]

    _nvim.api.set_current_win(focus_win)
    if layout is WindowLayout.LEFT:
        _nvim.api.set_option("splitright", False)
        _nvim.command(f"{size}vsplit")
    else:
        _nvim.api.set_option("splitbelow", True)
        _nvim.command(f"{size}split")

    _nvim.api.set_option("splitright", split_right)
    _nvim.api.set_option("splitbelow", split_below)

    window: Window = _nvim.api.get_current_win()
    return window


def win_set_buf(window: Window, buffer: Buffer) -> None:
    _nvim.api.win_set_buf(window, buffer)


def command(cmd: str) -> None:
    _nvim.api.command(cmd)


def set_current_win(window: Window) -> None:
    _nvim.api.set_current_win(window)


def get_global_var(name: str) -> Optional[str]:
    try:
        return _nvim.api.get_var(name)
    except:
        return None
