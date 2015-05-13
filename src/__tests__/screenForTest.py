# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

class ScreenForTest(object):

    """A dummy object that is dependency-injected in place
    of curses standard screen. Allows us to unit-test parts
    of the UI code"""

    def __init__(self, maxX=85, maxY=100):
        self.maxX = maxX
        self.maxY = maxY
        self.cursorX = 0
        self.cursorY = 0
        self.output = {}
        self.clear()

    def getmaxyx(self):
        return (self.maxY, self.maxX)

    def refresh(self):
        # TODO -- nothing to do here?
        pass

    def clear(self):
        self.output = {}
        for x in range(self.maxX):
            for y in range(self.maxY):
                coord = (x, y)
                self.output[coord] = ''

    def move(self, y, x):
        self.cursorY = y
        self.cursorX = x

    def getch(self):
        # TODO -- have a list of inputs?
        raise ValueError('No more characters provided in input')

