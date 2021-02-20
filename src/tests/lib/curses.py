# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


class CursesForTest:

    """The dependency-injected curses wrapper which simply
    stores some state in test runs of the UI"""

    def __init__(self):
        self.is_echo = False
        self.is_default_colors = False
        self.color_pairs = {}
        self.current_color = (0, 0)
        # the (0, 0) is hardcoded
        self.color_pairs[0] = self.current_color

    def use_default_colors(self):
        self.is_default_colors = True

    def echo(self):
        self.is_echo = True

    def noecho(self):
        self.is_echo = False

    def init_pair(self, pair_number, fg, bg):
        self.color_pairs[pair_number] = (fg, bg)

    def color_pair(self, color_number):
        self.current_color = self.color_pairs[color_number]
        # TOOD -- find a better return than this?
        return color_number

    def get_color_pairs(self):
        # pretend we are on 256 color
        return 256

    def exit(self):
        raise StopIteration("stopping program")

    def allow_file_output(self):
        # do not output selection pickle
        return False
