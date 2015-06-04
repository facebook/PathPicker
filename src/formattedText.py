# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
import re
import curses
from collections import namedtuple
from colorPrinter import ColorPrinter


class FormattedText(object):

    """A piece of ANSI escape formatted text which responds
    to str() returning the plain text and knows how to print
    itself out using ncurses"""

    ANSI_ESCAPE_FORMATTING = r'\x1b\[([^mK]*)[mK]'
    BOLD_ATTRIBUTE = 1
    UNDERLINE_ATTRIBUTE = 4
    Range = namedtuple('Range', 'bottom top')
    FOREGROUND_RANGE = Range(30, 39)
    BACKGROUND_RANGE = Range(40, 49)

    DEFAULT_COLOR_FOREGROUND = -1
    DEFAULT_COLOR_BACKGROUND = -1

    def __init__(self, text=None):
        self.text = text

        if not self.text is None:
            self.segments = re.split(self.ANSI_ESCAPE_FORMATTING, self.text)
            # re.split will insert a empty string if there is a match at the beginning
            # or it will return [string] if there is no match
            # create the invariant that every segment has a formatting segment, e.g
            # we will always have FORMAT, TEXT, FORMAT, TEXT
            self.segments.insert(0, '')
            self.plainText = ''.join(self.segments[1::2])

    def __str__(self):
        return self.plainText

    @classmethod
    def parseFormatting(cls, formatting):
        """Parse ANSI formatting; the formatting passed in should be
        stripped of the control characters and ending character"""
        fore = -1  # -1 default means "use default", not "use white/black"
        back = -1
        other = 0
        intValues = [int(value) for value in formatting.split(';') if value]
        for code in intValues:
            if (code >= cls.FOREGROUND_RANGE.bottom
                    and code <= cls.FOREGROUND_RANGE.top):
                fore = code - cls.FOREGROUND_RANGE.bottom
            elif (code >= cls.BACKGROUND_RANGE.bottom
                  and code <= cls.BACKGROUND_RANGE.top):
                back = code - cls.BACKGROUND_RANGE.bottom
            elif code == cls.BOLD_ATTRIBUTE:
                other = other | curses.A_BOLD
            elif code == cls.UNDERLINE_ATTRIBUTE:
                other = other | curses.A_UNDERLINE

        return (fore, back, other)

    @classmethod
    def getSequenceForAttributes(cls, fore, back, attr):
        """Return a fully formed escape sequence for the color pair
        and additional attributes"""
        return ("\x1b[" + str(cls.FOREGROUND_RANGE.bottom + fore)
                + ";" + str(cls.BACKGROUND_RANGE.bottom + back) + ";"
                + str(attr) + "m")

    def printText(self, y, x, printer, maxLen):
        """Print out using ncurses. Note that if any formatting changes
        occur, the attribute set is changed and not restored"""
        printedSoFar = 0
        for index, val in enumerate(self.segments):
            if printedSoFar >= maxLen:
                break
            if index % 2 == 1:
                # text
                toPrint = val[0:maxLen - printedSoFar]
                printer.addstr(y, x + printedSoFar, toPrint,
                               ColorPrinter.CURRENT_COLORS)
                printedSoFar += len(toPrint)
            else:
                # formatting
                printer.setAttributes(*self.parseFormatting(val))

    def findSegmentPlace(self, toGo):
        index = 1

        while index < len(self.segments):
            toGo -= len(self.segments[index])
            if toGo < 0:
                return (index, toGo)

            index += 2

        if toGo == 0:
            # we could reach here if the requested place is equal
            # to the very end of the string (as we do a <0 above).
            return (index - 2, len(self.segments[index - 2]))

    def breakat(self, where):
        """Break the formatted text at the point given and return
        a new tuple of two FormattedText representing the before and
        after"""
        #FORMAT, TEXT, FORMAT, TEXT, FORMAT, TEXT
        #--before----, segF,   seg,  ----after--
        #
        # to
        #
        #FORMAT, TEXT, FORMAT, TEXTBEFORE, FORMAT, TEXTAFTER, FORMAT, TEXT
        #--before----, segF,   [before],   segF,   [after],   -----after--
        #----index---------------/
        (index, splitPoint) = self.findSegmentPlace(where)
        textSegment = self.segments[index]
        beforeText = textSegment[:splitPoint]
        afterText = textSegment[splitPoint:]
        beforeSegments = self.segments[:index]
        afterSegments = self.segments[index + 1:]

        formattingForSegment = self.segments[index - 1]

        beforeFormattedText = FormattedText()
        afterFormattedText = FormattedText()
        beforeFormattedText.segments = (beforeSegments + [beforeText])
        afterFormattedText.segments = ([formattingForSegment]
                                       + [afterText] + afterSegments)
        beforeFormattedText.plainText = self.plainText[:where]
        afterFormattedText.plainText = self.plainText[where:]

        return (beforeFormattedText, afterFormattedText)
