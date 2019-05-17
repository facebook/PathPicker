# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import print_function

import sys
sys.path.insert(0, '../')
from charCodeMapping import CHAR_TO_CODE

ATTRIBUTE_SYMBOL_MAPPING = {
    0: ' ',
    1: ' ',
    2: 'B',
    2097154: '*',  # bold white
    131072: '_',
    3: 'G',
    4: 'R',
    5: '?',
    6: '!',
    2097153: 'W',
    2097155: '|',  # bold
    2097156: '/',  # bold
    2097158: '~',  # bold
    2097157: '@',  # bold
    7: '?',
}


class ScreenForTest(object):

    """A dummy object that is dependency-injected in place
    of curses standard screen. Allows us to unit-test parts
    of the UI code"""

    def __init__(self, charInputs, maxX, maxY):
        self.maxX = maxX
        self.maxY = maxY
        self.cursorX = 0
        self.cursorY = 0
        self.output = {}
        self.pastScreens = []
        self.charInputs = charInputs
        self.erase()
        self.currentAttribute = 0

    def getmaxyx(self):
        return (self.maxY, self.maxX)

    def refresh(self):
        if self.containsContent(self.output):
            # we have an old screen, so add it
            self.pastScreens.append(dict(self.output))

    def containsContent(self, screen):
        for coord, pair in screen.items():
            (char, attr) = pair
            if char:
                return True
        return False

    def erase(self):
        self.output = {}
        for x in range(self.maxX):
            for y in range(self.maxY):
                coord = (x, y)
                self.output[coord] = ('', 1)

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
            self.output[coord] = (string[deltaX], self.currentAttribute)

    def delch(self, y, x):
        '''Delete a character. We implement this by removing the output,
        NOT by printing a space'''
        self.output[(x, y)] = ('', 1)

    def getch(self):
        return CHAR_TO_CODE[self.charInputs.pop(0)]

    def getstr(self, y, x, maxLen):
        # TODO -- enable editing this
        return ''

    def printScreen(self):
        for index, row in enumerate(self.getRows()):
            print("Row %02d:%s" % (index, row))

    def printOldScreens(self):
        for oldScreen in range(self.getNumPastScreens()):
            for index, row in enumerate(self.getRowsForPastScreen(oldScreen)):
                print("Screen %02d Row %02d:%s" % (oldScreen, index, row))

    def getNumPastScreens(self):
        return len(self.pastScreens)

    def getRowsForPastScreen(self, pastScreen):
        return self.getRows(screen=self.pastScreens[pastScreen])

    def getRowsWithAttributesForPastScreen(self, pastScreen):
        return self.getRowsWithAttributes(screen=self.pastScreens[pastScreen])

    def getRowsWithAttributesForPastScreens(self, pastScreens):
        '''Get the rows & attributes for the array of screens as one stream
        (there is no extra new line or extra space between pages)'''
        pages = map(lambda screenIndex: self.getRowsWithAttributes(
            screen=self.pastScreens[screenIndex]), pastScreens)

        # join the pages together into one stream
        lines, attributes = zip(*pages)
        return ([line for page in lines for line in page],
                [line for page in attributes for line in page])

    def getRowsWithAttributes(self, screen=None):
        if not screen:
            screen = self.output

        rows = []
        attributeRows = []
        for y in range(self.maxY):
            row = ''
            attributeRow = ''
            for x in range(self.maxX):
                coord = (x, y)
                (char, attr) = screen[coord]
                row += char
                attributeRow += self.getAttributeSymbolForCode(attr)
            rows.append(row)
            attributeRows.append(attributeRow)
        return (rows, attributeRows)

    def getRows(self, screen=None):
        (rows, _) = self.getRowsWithAttributes(screen)
        return rows

    def getAttributeSymbolForCode(self, code):
        symbol = ATTRIBUTE_SYMBOL_MAPPING.get(code, None)
        if symbol is None:
            raise ValueError('%d not mapped' % code)
        return symbol
