# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Optional

from pathpicker.curses_api import CursesApiBase
from pathpicker.screen import ScreenBase


class ColorPrinter:

    """A thin wrapper over screens in ncurses that caches colors and
    attribute state"""

    DEFAULT_COLOR_INDEX = 1
    CURRENT_COLORS = -1

    def __init__(self, screen: ScreenBase, curses_api: CursesApiBase):
        self.colors = {}
        self.colors[(0, 0)] = 0  # 0,0 = white on black is hardcoded
        # in general, we want to use -1,-1 for most "normal" text printing
        self.colors[(-1, -1)] = self.DEFAULT_COLOR_INDEX
        self.curses_api = curses_api
        self.curses_api.init_pair(self.DEFAULT_COLOR_INDEX, -1, -1)
        self.screen = screen
        self.current_attributes = 0  # initialized in set_attributes

    def set_attributes(self, fg_color: int, bg_color: int, other: int) -> None:
        self.current_attributes = self.get_attributes(fg_color, bg_color, other)

    def get_attributes(self, fg_color: int, bg_color: int, other: int) -> int:
        color_index = -1
        color_pair = (fg_color, bg_color)
        if color_pair not in self.colors:
            new_index = len(self.colors)
            if new_index < self.curses_api.get_color_pairs():
                self.curses_api.init_pair(new_index, fg_color, bg_color)
                self.colors[color_pair] = new_index
                color_index = new_index
        else:
            color_index = self.colors[color_pair]

        attr = self.curses_api.color_pair(color_index)

        attr = attr | other

        return attr

    def addstr(
        self, y_pos: int, x_pos: int, text: str, attr: Optional[int] = None
    ) -> None:
        if attr is None:
            attr = self.curses_api.color_pair(self.DEFAULT_COLOR_INDEX)
        elif attr == self.CURRENT_COLORS:
            attr = self.current_attributes

        self.screen.addstr(y_pos, x_pos, text, attr)

    def clear_square(
        self, top_y: int, bottom_y: int, left_x: int, right_x: int
    ) -> None:
        # clear out square from top to bottom
        for i in range(top_y, bottom_y):
            self.clear_segment(i, left_x, right_x)

    # perhaps there's a more elegant way to do this
    def clear_segment(self, y_pos: int, start_x: int, end_x: int) -> None:
        space_str = " " * (end_x - start_x)
        attr = self.curses_api.color_pair(self.DEFAULT_COLOR_INDEX)

        self.screen.addstr(y_pos, start_x, space_str, attr)
