# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple
from .command_mode import run_command

if TYPE_CHECKING:
    import curses


class ScreenBase(ABC):
    @abstractmethod
    def getmaxyx(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def refresh(self) -> None:
        pass

    @abstractmethod
    def erase(self) -> None:
        pass

    @abstractmethod
    def move(self, y_pos: int, x_pos: int) -> None:
        pass

    @abstractmethod
    def addstr(self, y_pos: int, x_pos: int, string: str, attr: int) -> None:
        pass

    @abstractmethod
    def delch(self, y_pos: int, x_pos: int) -> None:
        pass

    @abstractmethod
    def getch(self) -> int:
        pass

    @abstractmethod
    def getstr(self, y_pos: int, x_pos: int, max_len: int) -> str:
        pass


class CursesScreen(ScreenBase):
    def __init__(self, screen: "curses._CursesWindow"):
        self.screen = screen

    def getmaxyx(self) -> Tuple[int, int]:
        return self.screen.getmaxyx()

    def refresh(self) -> None:
        self.screen.refresh()

    def erase(self) -> None:
        self.screen.erase()

    def move(self, y_pos: int, x_pos: int) -> None:
        self.screen.move(y_pos, x_pos)

    def addstr(self, y_pos: int, x_pos: int, string: str, attr: int) -> None:
        self.screen.addstr(y_pos, x_pos, string, attr)

    def delch(self, y_pos: int, x_pos: int) -> None:
        self.screen.delch(y_pos, x_pos)

    def getch(self) -> int:
        return self.screen.getch()

    def getstr(self, y_pos: int, x_pos: int, max_len: int) -> str:
        result = self.screen.getstr(y_pos, x_pos, max_len)
        if isinstance(result, str):
            return result
        if isinstance(result, int):
            return str(result)
        return result.decode("utf-8")
    
    def clrtoeol(self) -> None:
        """
        Clears from cursor to end of line using curses.
        """
        if hasattr(self.screen, "clrtoeol"):
            self.screen.clrtoeol()
        else:
            max_y, max_x = self.getmaxyx()
            y, x = self.screen.getyx()
            for _ in range(x, max_x):
                self.delch(y, x)
        self.refresh()

    def handle_command_mode(self, current_selection: str) -> None:
        """
        Trigger command mode for the selected file/directory.
        """
        self.addstr(0, 0, "Enter command: ", 0)
        self.refresh()
        cmd_input = self.getstr(0, 15, 100)  # read input from user

        # Run the command with token expansion
        run_command(cmd_input, current_selection, auto_mode=False)

        # Clear the input line after running
        self.move(0, 0)
        self.clrtoeol()
        self.refresh()

    def handle_input(self, current_selection: str) -> None:
        """
        Main input loop for the screen.
        """
        while True:
            key = self.getch()

            if key in (ord('q'), ord('Q')):
                break  # quit
            elif key == ord(':'):
                # Enter command mode
                self.handle_command_mode(current_selection)
            # Add other key handling here, e.g., navigation
