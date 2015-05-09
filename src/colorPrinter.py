# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint
import curses

class ColorPrinter(object):
    """A thin wrapper over screens in ncurses that caches colors and
    attribute state"""
    def __init__(self, screen):
        self.colors = {}
        self.colors[(0,0)] = 0 #0,0 = white on black is hardcoded
        self.screen = screen


    def setAttributes(self, foreColor, backColor, other):
        colorIndex = -1
        colorPair = (foreColor, backColor)
        if not colorPair in self.colors:
            newIndex = len(self.colors)
            if newIndex < curses.COLOR_PAIRS:
                curses.init_pair(newIndex, foreColor, backColor)
                self.colors[colorPair] = newIndex
                colorIndex = newIndex
        else:
            colorIndex = self.colors[colorPair]

        attr = curses.color_pair(colorIndex)
        attr = attr | other

        self.currentAttributes = attr

        self.screen.attrset(self.currentAttributes)

    def restoreAttributes(self):
        self.screen.attrset(self.currentAttributes)
