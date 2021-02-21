# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


class CursesForTest:

    """The dependency-injected curses wrapper which simply
    stores some state in test runs of the UI"""

    def __init__(self) -> None:
        self.is_echo = False
        self.is_default_colors = False
        self.color_pairs = {}
        self.current_color = (0, 0)
        # the (0, 0) is hardcoded
        self.color_pairs[0] = self.current_color

    def use_default_colors(self) -> None:
        self.is_default_colors = True

    def echo(self) -> None:
        self.is_echo = True

    def noecho(self) -> None:
        self.is_echo = False

    def init_pair(self, pair_number: int, fg_color: int, bg_color: int) -> None:
        self.color_pairs[pair_number] = (fg_color, bg_color)

    def color_pair(self, color_number: int) -> int:
        self.current_color = self.color_pairs[color_number]
        # TODO -- find a better return than this?
        return color_number

    def get_color_pairs(self) -> int:
        # pretend we are on 256 color
        return 256

    def exit(self) -> None:
        raise StopIteration("stopping program")

    def allow_file_output(self) -> bool:
        # do not output selection pickle
        return False
