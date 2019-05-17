# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from __future__ import print_function


class CursesForTest(object):

    """The dependency-injected curses wrapper which simply
    stores some state in test runs of the UI"""

    def __init__(self):
        self.isEcho = False
        self.isDefaultColors = False
        self.colorPairs = {}
        self.currentColor = (0, 0)
        # the (0, 0) is hardcoded
        self.colorPairs[0] = self.currentColor

    def useDefaultColors(self):
        self.isDefaultColors = True

    def echo(self):
        self.isEcho = True

    def noecho(self):
        self.isEcho = False

    def initPair(self, pairNumber, fg, bg):
        self.colorPairs[pairNumber] = (fg, bg)

    def colorPair(self, colorNumber):
        self.currentColor = self.colorPairs[colorNumber]
        # TOOD -- find a better return than this?
        return colorNumber

    def getColorPairs(self):
        # pretend we are on 256 color
        return 256

    def exit(self):
        raise StopIteration('stopping program')

    def allowFileOutput(self):
        # do not output selection pickle
        return False
