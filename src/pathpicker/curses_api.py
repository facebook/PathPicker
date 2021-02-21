# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import sys
from abc import ABC, abstractmethod


class CursesApiBase(ABC):
    @abstractmethod
    def use_default_colors(self) -> None:
        pass

    @abstractmethod
    def echo(self) -> None:
        pass

    @abstractmethod
    def noecho(self) -> None:
        pass

    @abstractmethod
    def init_pair(self, pair_number: int, fg_color: int, bg_color: int) -> None:
        pass

    @abstractmethod
    def color_pair(self, color_number: int) -> int:
        pass

    @abstractmethod
    def get_color_pairs(self) -> int:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    @abstractmethod
    def allow_file_output(self) -> bool:
        pass


class CursesApi(CursesApiBase):

    """A dummy curses wrapper that allows us to intercept these
    calls when in a test environment"""

    def use_default_colors(self) -> None:
        curses.use_default_colors()

    def echo(self) -> None:
        curses.echo()

    def noecho(self) -> None:
        curses.noecho()

    def init_pair(self, pair_number: int, fg_color: int, bg_color: int) -> None:
        curses.init_pair(pair_number, fg_color, bg_color)

    def color_pair(self, color_number: int) -> int:
        return curses.color_pair(color_number)

    def get_color_pairs(self) -> int:
        assert hasattr(curses, "COLOR_PAIRS"), "curses is not initialized!"
        return curses.COLOR_PAIRS

    def exit(self) -> None:
        sys.exit(0)

    def allow_file_output(self) -> bool:
        return True
