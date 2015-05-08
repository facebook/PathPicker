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

import parse


class SimpleLine(object):

    def __init__(self, line, index):
        self.line = line
        self.index = index
        self.controller = None

    def printOut(self):
        print(str(self))

    def output(self, stdscr):
        (minx, miny, maxx, maxy) = self.controller.getChromeBoundaries()
        maxLen = maxx - minx
        y = miny + self.index + self.controller.getScrollOffset()
        try:
            stdscr.addstr(y, minx, str(self)[0:maxLen])
        except curses.error:
            pass

    def __str__(self):
        return self.line


class LineMatch(object):

    def __init__(self, line, result, index):
        self.line = line
        self.index = index

        file, num, matches = result

        self.originalFile = file
        self.file = parse.prependDir(file)
        self.number = num
        # save a bunch of stuff so we can
        # pickle
        self.start = matches.start()
        self.end = min(matches.end(), len(line))
        group = matches.group()

        # this is a bit weird but we need to strip
        # off the whitespace for the matches we got,
        # since matches like README are aggressive
        # about including whitespace. For most lines
        # this will be a no-op, but for lines like
        # "README        " we will reset end to
        # earlier
        stringSubset = line[self.start:self.end]
        strippedSubset = stringSubset.strip()
        trailingWhitespace = len(stringSubset) - len(strippedSubset)
        self.end -= trailingWhitespace
        self.group = group[:-trailingWhitespace]

        self.selected = False
        self.hovered = False

        self.controller = None

    def toggleSelect(self):
        self.selected = not self.selected

    def setSelect(self, val):
        self.selected = val

    @property
    def directory(self):
        # for the cd command and the like. file is a string like
        # ./asd.py or ~/www/asdasd/dsada.php, so since it already
        # has the directory appended we can just split on / and drop
        # the last
        parts = self.file.split('/')[0:-1]
        return '/'.join(parts)

    def isResolvable(self):
        return not self.isGitAbbreviatedPath()

    def isGitAbbreviatedPath(self):
        # this method mainly serves as a warning for when we get
        # git-abbrievated paths like ".../" that confuse users.
        parts = self.file.split('/')
        if len(parts) and parts[0] == '...':
            return True
        return False

    @property
    def before(self):
        return self.line[0:self.start]

    @property
    def after(self):
        return self.line[self.end:]

    def getMatch(self):
        return self.group

    def __str__(self):
        return self.before + '||' + self.getMatch(
        ) + '||' + self.after + '||' + str(self.number)

    def getStyleForState(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)

        if self.hovered and self.selected:
            return curses.color_pair(3)
        elif self.hovered:
            return curses.color_pair(1)
        elif self.selected:
            return curses.color_pair(2)
        else:
            return curses.A_UNDERLINE

    def getDecorator(self):
        if self.selected:
            return '|===>'
        return ''

    def output(self, stdscr):
        decorator = self.getDecorator()
        before = self.before
        after = self.after
        middle = ''.join([decorator, self.getMatch()])
        (minx, miny, maxx, maxy) = self.controller.getChromeBoundaries()
        y = miny + self.index + self.controller.getScrollOffset()

        if (y < miny or y > maxy):
            # wont be displayed!
            return

        maxLen = maxx - minx
        try:
            # beginning
            stdscr.addstr(y, minx, before)
            # bolded middle
            xIndex = len(before)
            stdscr.addstr(y, minx + xIndex, middle[0:max(maxLen - xIndex, 0)],
                          self.getStyleForState())
            # end
            xIndex = len(before) + len(middle)
            stdscr.addstr(y, minx + xIndex, after[0:max(maxLen - xIndex, 0)])
        except curses.error:
            pass
