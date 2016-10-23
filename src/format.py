# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import os
import time
import subprocess

import curses
import parse
from formattedText import FormattedText


class SimpleLine(object):

    def __init__(self, formattedLine, index):
        self.formattedLine = formattedLine
        self.index = index
        self.controller = None

    def printOut(self):
        print(str(self))

    def output(self, printer):
        (minx, miny, maxx, maxy) = self.controller.getChromeBoundaries()
        maxLen = min(maxx - minx, len(str(self)))
        y = miny + self.index + self.controller.getScrollOffset()

        if (y < miny or y >= maxy):
            # wont be displayed!
            return

        self.formattedLine.printText(y, minx, printer, maxLen)

    def __str__(self):
        return str(self.formattedLine)

    def isSimple(self):
        return True


class LineMatch(object):

    ARROW_DECORATOR = '|===>'
    # this is inserted between long files, so it looks like
    # ./src/foo/bar/something|...|baz/foo.py
    TRUNCATE_DECORATOR = '|...|'

    def __init__(self, formattedLine, result, index, validateFileExists=False, allInput=False):
        self.controller = None

        self.formattedLine = formattedLine
        self.index = index
        self.allInput = allInput

        (path, num, matches) = result

        self.originalPath = path
        self.path = path if allInput else parse.prependDir(path,
                                                           withFileInspection=validateFileExists)
        self.num = num

        line = str(self.formattedLine)
        # save a bunch of stuff so we can
        # pickle
        self.start = matches.start()
        self.end = min(matches.end(), len(line))
        self.group = matches.group()

        # this is a bit weird but we need to strip
        # off the whitespace for the matches we got,
        # since matches like README are aggressive
        # about including whitespace. For most lines
        # this will be a no-op, but for lines like
        # "README        " we will reset end to
        # earlier
        stringSubset = line[self.start:self.end]
        strippedSubset = stringSubset.strip()
        trailingWhitespace = (len(stringSubset) - len(strippedSubset))
        self.end -= trailingWhitespace
        self.group = self.group[0:len(self.group) - trailingWhitespace]

        self.selected = False
        self.hovered = False
        self.isTruncated = False

        # precalculate the pre, post, and match strings
        (self.beforeText, unused) = self.formattedLine.breakat(self.start)
        (unused, self.afterText) = self.formattedLine.breakat(self.end)

        self.updateDecoratedMatch()

    def toggleSelect(self):
        self.setSelect(not self.selected)

    def setSelect(self, val):
        self.selected = val
        self.updateDecoratedMatch()

    def setHover(self, val):
        self.hovered = val
        self.updateDecoratedMatch()

    def getScreenIndex(self):
        return self.index

    def getPath(self):
        return self.path

    def getSizeInBytes(self):
        bashCommand = "ls -lh " + self.path
        output = subprocess.check_output(bashCommand.split())
        size = output.split()[4]
        return 'size: ' + str(size)

    def getLengthInLines(self):
        bashCommand = "wc -l " + self.path
        output = subprocess.check_output(bashCommand.split())
        return 'length: ' + str(output.strip().split()[0]) + ' lines'

    def getTimeLastAccessed(self):
        timeAccessed = time.strftime(
            '%m/%d/%Y %H:%M:%S', time.localtime(os.stat(self.path).st_atime))
        return 'last accessed: ' + timeAccessed

    def getTimeLastModified(self):
        timeModified = time.strftime(
            '%m/%d/%Y %H:%M:%S', time.localtime(os.stat(self.path).st_mtime))
        return 'last modified: ' + timeModified

    def getOwnerUser(self):
        bashCommand = "ls -ld " + self.path
        output = subprocess.check_output(bashCommand.split())
        userOwnerName = output.split()[2]
        userOwnerId = os.stat(self.path).st_uid
        return 'owned by user: ' + str(userOwnerName) + ', ' + str(userOwnerId)

    def getOwnerGroup(self):
        bashCommand = "ls -ld " + self.path
        output = subprocess.check_output(bashCommand.split())
        groupOwnerName = output.split()[3]
        groupOwnerId = os.stat(self.path).st_gid
        return 'owned by group: ' + str(groupOwnerName) + ', ' + str(groupOwnerId)

    def getDir(self):
        # for the cd command and the like. file is a string like
        # ./asd.py or ~/www/asdasd/dsada.php, so since it already
        # has the directory appended we can just split on / and drop
        # the last
        parts = self.path.split('/')[0:-1]
        return '/'.join(parts)

    def isResolvable(self):
        return not self.isGitAbbreviatedPath()

    def isGitAbbreviatedPath(self):
        # this method mainly serves as a warning for when we get
        # git-abbrievated paths like ".../" that confuse users.
        parts = self.path.split('/')
        if len(parts) and parts[0] == '...':
            return True
        return False

    def getLineNum(self):
        return self.num

    def isSimple(self):
        return False

    def getSelected(self):
        return self.selected

    def getBefore(self):
        return str(self.beforeText)

    def getAfter(self):
        return str(self.afterText)

    def getMatch(self):
        return self.group

    def __str__(self):
        return (self.getBefore() + '||' + self.getMatch()
                + '||' + self.getAfter() + '||' +
                str(self.num))

    def updateDecoratedMatch(self, maxLen=None):
        '''Update the cached decorated match formatted string, and
        dirty the line, if needed'''
        if self.hovered and self.selected:
            attributes = (curses.COLOR_WHITE, curses.COLOR_RED,
                          FormattedText.BOLD_ATTRIBUTE)
        elif self.hovered:
            attributes = (curses.COLOR_WHITE, curses.COLOR_BLUE,
                          FormattedText.BOLD_ATTRIBUTE)
        elif self.selected:
            attributes = (curses.COLOR_WHITE, curses.COLOR_GREEN,
                          FormattedText.BOLD_ATTRIBUTE)
        elif not self.allInput:
            attributes = (0, 0, FormattedText.UNDERLINE_ATTRIBUTE)
        else:
            attributes = (0, 0, 0)

        decoratorText = self.getDecorator()

        # we may not be connected to a controller (during processInput,
        # for example)
        if self.controller:
            self.controller.dirtyLine(self.index)

        plainText = decoratorText + self.getMatch()
        if maxLen and len(plainText + str(self.beforeText)) > maxLen:
            # alright, we need to chop the ends off of our
            # decorated match and glue them together with our
            # truncation decorator. We subtract the length of the
            # before text since we consider that important too.
            spaceAllowed = maxLen - len(self.TRUNCATE_DECORATOR) \
                - len(decoratorText) \
                - len(str(self.beforeText))
            midPoint = int(spaceAllowed / 2)
            beginMatch = plainText[0:midPoint]
            endMatch = plainText[-midPoint:len(plainText)]
            plainText = beginMatch + self.TRUNCATE_DECORATOR + endMatch

        self.decoratedMatch = FormattedText(
            FormattedText.getSequenceForAttributes(*attributes) +
            plainText)

    def getDecorator(self):
        if self.selected:
            return self.ARROW_DECORATOR
        return ''

    def printUpTo(self, text, printer, y, x, maxLen):
        '''Attempt to print maxLen characters, returning a tuple
        (x, maxLen) updated with the actual number of characters
        printed'''
        if maxLen <= 0:
            return (x, maxLen)

        maxPrintable = min(len(str(text)), maxLen)
        text.printText(y, x, printer, maxPrintable)
        return (x + maxPrintable, maxLen - maxPrintable)

    def output(self, printer):
        (minx, miny, maxx, maxy) = self.controller.getChromeBoundaries()
        y = miny + self.index + self.controller.getScrollOffset()

        if (y < miny or y >= maxy):
            # wont be displayed!
            return

        # we dont care about the after text, but we should be able to see
        # all of the decorated match (which means we need to see up to
        # the end of the decoratedMatch, aka include beforeText)
        importantTextLength = len(str(self.beforeText)) + \
            len(str(self.decoratedMatch))
        spaceForPrinting = maxx - minx
        if importantTextLength > spaceForPrinting:
            # hrm, we need to update our decorated match to show
            # a truncated version since right now we will print off
            # the screen. lets also dump the beforeText for more
            # space
            self.updateDecoratedMatch(maxLen=spaceForPrinting)
            self.isTruncated = True
        else:
            # first check what our expanded size would be:
            expandedSize = len(str(self.beforeText)) + \
                len(self.getMatch())
            if expandedSize < spaceForPrinting and self.isTruncated:
                # if the screen gets resized, we might be truncated
                # from a previous render but **now** we have room.
                # in that case lets expand back out
                self.updateDecoratedMatch()
                self.isTruncated = False

        maxLen = maxx - minx
        soFar = (minx, maxLen)

        soFar = self.printUpTo(self.beforeText, printer, y, *soFar)
        soFar = self.printUpTo(self.decoratedMatch, printer, y, *soFar)
        soFar = self.printUpTo(self.afterText, printer, y, *soFar)
