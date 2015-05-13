# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
sys.path.insert(0,'../')
from charCodeMapping import CHAR_TO_CODE

class ScreenForTest(object):

    """A dummy object that is dependency-injected in place
    of curses standard screen. Allows us to unit-test parts
    of the UI code"""

    def __init__(self, charInputs, maxX=80, maxY=30):
        self.maxX = maxX
        self.maxY = maxY
        self.cursorX = 0
        self.cursorY = 0
        self.output = {}
        self.charInputs = charInputs
        self.clear()
        self.currentAttribute = 0

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

    def attrset(self, attr):
        self.currentAttribute = attr

    def addstr(self, y, x, string, attr=None):
        if attr:
            self.attrset(attr)
        for deltaX in range(len(string)):
            coord = (x + deltaX, y)
            self.output[coord] = string[deltaX]

    def getch(self):
        return CHAR_TO_CODE[self.charInputs.pop(0)]

    def printScreen(self):
        for index, row in enumerate(self.getRows()):
            print("Row %02d:%s" % (index, row))

    def getRows(self):
        rows = []
        for y in range(self.maxY):
            row = ''
            for x in range(self.maxX):
                coord = (x, y)
                row += self.output.get(coord, ' ')
            rows.append(row)
        return rows
