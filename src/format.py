# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint
from __future__ import print_function

import curses

from utils import ignore_curse_errors
import parse


class SimpleLine(object):

    def __init__(self, line, index):
        self.line = line
        self.index = index

    # TODO: Change the name of this method ? Like `write_output` ?
    def output(self, controller):
        # TODO: Maybe add methods to the controller to access `stdscr`
        stdscr = controller.stdscr

        minx, miny, maxx, _ = controller.getChromeBoundaries()
        max_len = maxx - minx
        y = miny + self.index + controller.getScrollOffset()
        with ignore_curse_errors():
            stdscr.addstr(y, minx, str(self)[:max_len])

    def __str__(self):
        return self.line


class LineMatch(object):
    # Foreground/Background pair numbers.
    HOVERED = 1
    SELECTED = 2
    HOVERED_AND_SELECTED = 3

    def __init__(self, line, result, index):
        self.line = line
        self.index = index

        file, num, matches = result

        self.file = parse.prependDir(file)
        self.number = num
        # save a bunch of stuff so we can
        # pickle
        self.start = matches.start()
        end = min(matches.end(), len(line))
        group = matches.group()

        # this is a bit weird but we need to strip
        # off the whitespace for the matches we got,
        # since matches like README are aggressive
        # about including whitespace. For most lines
        # this will be a no-op, but for lines like
        # "README        " we will reset end to
        # earlier
        string_subset = line[self.start:end]
        stripped_subset = string_subset.strip()
        trailing_whitespace = len(string_subset) - len(stripped_subset)
        self.end = end - trailing_whitespace
        if trailing_whitespace:
            self.match = group[:-trailing_whitespace]
        else:
            self.match = group

        self.is_selected = False
        self.is_hovered = False

    def toggle_select(self):
        self.is_selected = not self.is_selected

    @property
    def directory(self):
        # for the cd command and the like. file is a string like
        # ./asd.py or ~/www/asdasd/dsada.php, so since it already
        # has the directory appended we can just split on / and drop
        # the last
        parts = self.file.split('/')[0:-1]
        return '/'.join(parts)

    @property
    def is_resolvable(self):
        return not self.is_git_abbreviated_path

    @property
    def is_git_abbreviated_path(self):
        # this method mainly serves as a warning for when we get
        # git-abbrievated paths like ".../" that confuse users.
        parts = self.file.split('/')
        try:
            return parts[0] == '...'
        except IndexError:
            return False

    @property
    def before(self):
        return self.line[0:self.start]

    @property
    def after(self):
        return self.line[self.end:]

    def __str__(self):
        parts = [self.before, self.match, self.after, str(self.number)]
        return '||'.join(parts)

    # TODO: This might not be the most appropriate place to put this method.
    # But still, it's better than before.
    def set_color_pairs(self):
        """
        Set the different color pairs:
        - The background/foreground for the hovered case.
        - The background/foreground for the selected case.
        - The background/foreground for the hovered and selected case.
        """
        curses.init_pair(self.HOVERED, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(self.SELECTED, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(self.HOVERED_AND_SELECTED, curses.COLOR_WHITE,
                         curses.COLOR_GREEN)

    @property
    def color_pair(self):
        """
        Color pair for the current line's state.

        /!\ Side effects. You must call :meth:`set_color_pairs` before
        accessing this attribute.
        """
        if self.is_hovered and self.is_selected:
            return curses.color_pair(self.HOVERED_AND_SELECTED)
        elif self.is_hovered:
            return curses.color_pair(self.HOVERED)
        elif self.is_selected:
            return curses.color_pair(self.SELECTED)
        else:
            return curses.A_UNDERLINE

    # TODO: Maybe find a better name, since the name is ambiguous.
    @property
    def decorator(self):
        if self.is_selected:
            return '|===>'
        return ''

    # TODO: Change the name of this method ? Like `write_output` ?
    def output(self, controller):
        # TODO: Maybe add methods to the controller to access `stdscr`
        stdscr = controller.stdscr
        decorator = self.decorator
        before = self.before
        after = self.after
        middle = decorator + self.match
        minx, miny, maxx, maxy = controller.getChromeBoundaries()
        y = miny + self.index + controller.getScrollOffset()

        if y < miny or y > maxy:
            # wont be displayed!
            return

        max_len = maxx - minx
        with ignore_curse_errors():
            # beginning
            stdscr.addstr(y, minx, before)
            # bolded middle
            x_index = len(before)

            self.set_color_pairs()
            stdscr.addstr(y, minx + x_index, middle[:max(max_len - x_index, 0)],
                          self.color_pair)
            # end
            x_index = len(before) + len(middle)
            stdscr.addstr(y, minx + x_index, after[:max(max_len - x_index, 0)])
