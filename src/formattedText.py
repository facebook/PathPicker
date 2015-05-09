# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint

import re
import curses

class FormattedText(object):
    """A piece of ANSI escape formatted text which responds
    to str() returning the plain text and knows how to print
    itself out using ncurses"""

    ANSI_ESCAPE_FORMATTING = r'\x1b\[([^mK]*)[mK]'
    BOLD_ATTRIBUTE = 1
    UNDERLINE_ATTRIBUTE = 4

    def __init__(self, text):
        self.text = text

        self.segments = re.split(self.ANSI_ESCAPE_FORMATTING, self.text)
        #re.split will insert a empty string if there is a match at the beginning
        #or it will return [string] if there is no match
        #create the invariant that every segment has a formatting segment, e.g
        #we will always have FORMAT, TEXT, FORMAT, TEXT
        self.segments.insert(0, '')
        self.plainText = ''.join(self.segments[1::2])


    def __str__(self):
        return self.plainText

    @classmethod
    def parseFormatting(cls, formatting):
        """Parse ANSI formatting; the formatting passed in should be
        stripped of the control characters and ending character"""
        fore = -1 #-1 default means "use default", not "use white/black"
        back = -1
        other = 0
        intValues = [int(value) for value in formatting.split(';') if value]
        for code in intValues:
            if code >= 30 and code <= 39:
                fore = code-30
            elif code >= 40 and code <= 49:
                back = code-40
            elif code == cls.BOLD_ATTRIBUTE:
                other = other | curses.A_BOLD
            elif code == cls.UNDERLINE_ATTRIBUTE:
                other = other | curses.A_UNDERLINE

        return (fore, back, other)

    @staticmethod
    def getSequenceForAttributes(fore, back, attr):
        """Return a fully formed escape sequence for the color pair
        and additional attributes"""
        return "\x1b["+str(30+fore)+";"+str(40+back)+";"+str(attr)+"m"

    def printText(self, y, x, printer, maxLen):
        """Print out using ncurses. Note that if any formatting changes
        occur, the attribute set is changed and not restored"""
        printedSoFar = 0
        for index, val in enumerate(self.segments):
            if index % 2 == 1:
                #text
                toPrint = val[0:maxLen-printedSoFar]
                printer.screen.addstr(y, x + printedSoFar, toPrint)
                printedSoFar += len(toPrint)
            else:
                #formatting
                printer.setAttributes(*self.parseFormatting(val))


    def findSegmentPlace(self, toGo):
        index = 1
        while index < len(self.segments):
            toGo -= len(self.segments[index])
            if toGo < 0:
                return (index, toGo)

            index += 2

    def breakat(self, toGo):
        """Break the line at the point given and replicate
        the formatting"""
        #FORMAT, TEXT, FORMAT, TEXT, FORMAT, TEXT
        #--before----, segF,   seg,  ----after--
        #
        # to
        #
        #FORMAT, TEXT, FORMAT, TEXTBEFORE, FORMAT, TEXTAFTER, FORMAT, TEXT
        #--before----, segF,   [before],   segF,   [after],   -----after--
        #----index---------------/
        (index, toGo) = self.findSegmentPlace(toGo)
        textSegment = self.segments[index]
        beforeText = textSegment[:toGo]
        afterText = textSegment[toGo:]
        beforeSegments = self.segments[:index]
        afterSegments = self.segments[index+1:]

        formattingForSegment = self.segments[index-1]

        self.segments = (beforeSegments + [beforeText]
                         + [formattingForSegment]
                         + [afterText] + afterSegments)

    def replace(self, start, end, newString):
        """replace some text in the formatted text with some new text.
        the start and end indices index into the string ignoring the
        formatting"""
        newFormattedString = FormattedText(newString)

        self.breakat(start)
        self.breakat(end)

        (startSegmentIndex, startPlace) = self.findSegmentPlace(start)
        (endSegmentIndex, endPlace) = self.findSegmentPlace(end)

        newSegments = (self.segments[:startSegmentIndex-1]
                       + newFormattedString.segments
                       + self.segments[endSegmentIndex-1:])

        self.segments = newSegments
