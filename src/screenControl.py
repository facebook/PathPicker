# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function
import curses
import sys
import signal

import processInput
import usageStrings
import output
import logger
import format
from charCodeMapping import CODE_TO_CHAR
from colorPrinter import ColorPrinter


def signal_handler(signal, frame):
    # from http://stackoverflow.com/a/1112350/948126
    # Lets just quit rather than signal.SIGINT printing the stack
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


CHROME_MIN_X = 5
CHROME_MIN_Y = 0

SELECT_MODE = 'SELECT'
COMMAND_MODE = 'COMMAND_MODE'
X_MODE = 'X_MODE'

lbls = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~!@#$%^&*()_+<>?{}|;'"

# options for displayed to the user at the bottom of the screen
SHORT_NAV_OPTION_SELECTION_STR = '[f|A] selection'
SHORT_NAV_OPTION_NAVIGATION_STR = '[down|j|up|k|space|b] navigation'
SHORT_NAV_OPTION_OPEN_STR = '[enter] open'
SHORT_NAV_OPTION_QUICK_SELECT_STR = '[x] quick select mode'
SHORT_NAV_OPTION_COMMAND_STR = '[c] command mode'

SHORT_COMMAND_USAGE = 'command examples: | git add | git checkout HEAD~1 -- | mv $F ../here/ |'
SHORT_COMMAND_PROMPT = 'Type a command below! Paths will be appended or replace $F'
SHORT_COMMAND_PROMPT2 = 'Enter a blank line to go back to the selection process'
SHORT_PATHS_HEADER = 'Paths you have selected:'

INVISIBLE_CURSOR = 0
BLOCK_CURSOR = 2


class HelperChrome(object):

    def __init__(self, printer, screenControl, flags):
        self.printer = printer
        self.screenControl = screenControl
        self.flags = flags
        self.WIDTH = 50
        self.SIDEBAR_Y = 0
        self.DESCRIPTION_CLEAR = True
        if self.getIsSidebarMode():
            logger.addEvent('init_wide_mode')
        else:
            logger.addEvent('init_narrow_mode')

    def output(self, mode):
        self.mode = mode
        for func in [self.outputSide, self.outputBottom, self.toggleCursor]:
            try:
                func()
            except curses.error:
                pass

    def outputDescription(self, lineObj):
        self.outputDescriptionPane(lineObj)

    def toggleCursor(self):
        # only include cursor when in command mode
        if self.mode == COMMAND_MODE:
            curses.curs_set(BLOCK_CURSOR)
        else:
            curses.curs_set(INVISIBLE_CURSOR)

    def reduceMaxY(self, maxy):
        if self.getIsSidebarMode():
            return maxy
        return maxy - 4

    def reduceMaxX(self, maxx):
        if not self.getIsSidebarMode():
            return maxx
        return maxx - self.WIDTH

    def getMinX(self):
        if self.mode == COMMAND_MODE:
            return 0
        return self.screenControl.getChromeBoundaries()[0]

    def getMinY(self):
        return self.screenControl.getChromeBoundaries()[1]

    def getIsSidebarMode(self):
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        return maxx > 200

    def trimLine(self, str, width):
        return str[:width]

    def outputDescriptionPane(self, lineObj):
        if not self.getIsSidebarMode():
            return
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        borderX = maxx - self.WIDTH
        startY = self.SIDEBAR_Y + 1
        startX = borderX + 2
        headerLine = 'Description for ' + lineObj.path + ' :'
        linePrefix = '    * '
        descLines = [
            lineObj.getTimeLastAccessed(),
            lineObj.getTimeLastModified(),
            lineObj.getOwnerUser(),
            lineObj.getOwnerGroup(),
            lineObj.getSizeInBytes(),
            lineObj.getLengthInLines()
        ]
        self.printer.addstr(startY, startX, headerLine)
        y = startY + 2
        for descLine in descLines:
            descLine = self.trimLine(descLine, maxx - startX - len(linePrefix))
            self.printer.addstr(y, startX, linePrefix + descLine)
            y = y + 1
        self.DESCRIPTION_CLEAR = False

    # to fix bug where description pane may not clear on scroll
    def clearDescriptionPane(self):
        if self.DESCRIPTION_CLEAR:
            return
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        borderX = maxx - self.WIDTH
        startY = self.SIDEBAR_Y + 1
        self.printer.clearSquare(startY, maxy - 1, borderX + 2, maxx)
        self.DESCRIPTION_CLEAR = True

    def outputSide(self):
        if not self.getIsSidebarMode():
            return
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        borderX = maxx - self.WIDTH
        if (self.mode == COMMAND_MODE):
            borderX = len(SHORT_COMMAND_PROMPT) + 20
        usageLines = usageStrings.USAGE_PAGE.split('\n')
        if self.mode == COMMAND_MODE:
            usageLines = usageStrings.USAGE_COMMAND.split('\n')
        for index, usageLine in enumerate(usageLines):
            self.printer.addstr(self.getMinY() + index, borderX + 2, usageLine)
            self.SIDEBAR_Y = self.getMinY() + index
        for y in range(self.getMinY(), maxy):
            self.printer.addstr(y, borderX, '|')

    def outputBottom(self):
        if self.getIsSidebarMode():
            return
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        borderY = maxy - 2
        # first output text since we might throw an exception during border
        usageStr = {
            SELECT_MODE: self.getShortNavUsageString(),
            X_MODE: self.getShortNavUsageString(),
            COMMAND_MODE: SHORT_COMMAND_USAGE
        }[self.mode]
        borderStr = '_' * (maxx - self.getMinX() - 0)
        self.printer.addstr(borderY, self.getMinX(), borderStr)
        self.printer.addstr(borderY + 1, self.getMinX(), usageStr)

    def getShortNavUsageString(self):
        navOptions = [SHORT_NAV_OPTION_SELECTION_STR,
                      SHORT_NAV_OPTION_NAVIGATION_STR,
                      SHORT_NAV_OPTION_OPEN_STR,
                      SHORT_NAV_OPTION_QUICK_SELECT_STR,
                      SHORT_NAV_OPTION_COMMAND_STR]

        # it does not make sense to give the user the option to "open" the selection
        # in all-input mode
        if self.flags.getAllInput():
            navOptions.remove(SHORT_NAV_OPTION_OPEN_STR)

        return ', '.join(navOptions)


class ScrollBar(object):

    def __init__(self, printer, lines, screenControl):
        self.printer = printer
        self.screenControl = screenControl
        self.numLines = len(lines)
        self.boxStartFraction = 0.0
        self.boxStopFraction = 0.0
        self.calcBoxFractions()

        # see if we are activated
        self.activated = True
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        if (self.numLines < maxy):
            self.activated = False
            logger.addEvent('no_scrollbar')
        else:
            logger.addEvent('needed_scrollbar')

    def getIsActivated(self):
        return self.activated

    def calcBoxFractions(self):
        # what we can see is basically the fraction of our screen over
        # total num lines
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        fracDisplayed = min(1.0, (maxy / float(self.numLines)))
        self.boxStartFraction = -self.screenControl.getScrollOffset() / float(
            self.numLines)
        self.boxStopFraction = self.boxStartFraction + fracDisplayed

    def output(self):
        if not self.activated:
            return
        for func in [self.outputCaps, self.outputBase, self.outputBox,
                     self.outputBorder]:
            try:
                func()
            except curses.error:
                pass

    def getMinY(self):
        return self.screenControl.getChromeBoundaries()[1] + 1

    def getX(self):
        return 0

    def outputBorder(self):
        x = self.getX() + 4
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        for y in range(0, maxy):
            self.printer.addstr(y, x, ' ')

    def outputBox(self):
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        topY = maxy - 2
        minY = self.getMinY()
        diff = topY - minY
        x = self.getX()

        boxStartY = int(diff * self.boxStartFraction) + minY
        boxStopY = int(diff * self.boxStopFraction) + minY

        self.printer.addstr(boxStartY, x, '/-\\')
        for y in range(boxStartY + 1, boxStopY):
            self.printer.addstr(y, x, '|-|')
        self.printer.addstr(boxStopY, x, '\-/')

    def outputCaps(self):
        x = self.getX()
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        for y in [self.getMinY() - 1, maxy - 1]:
            self.printer.addstr(y, x, '===')

    def outputBase(self):
        x = self.getX()
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        for y in range(self.getMinY(), maxy - 1):
            self.printer.addstr(y, x, ' . ')


class Controller(object):

    def __init__(self, flags, stdscr, lineObjs, cursesAPI):
        self.stdscr = stdscr
        self.cursesAPI = cursesAPI
        self.cursesAPI.useDefaultColors()
        self.colorPrinter = ColorPrinter(self.stdscr, cursesAPI)
        self.flags = flags

        self.lineObjs = lineObjs
        self.hoverIndex = 0
        self.scrollOffset = 0
        self.scrollBar = ScrollBar(self.colorPrinter, lineObjs, self)
        self.helperChrome = HelperChrome(self.colorPrinter, self, flags)
        (self.oldmaxy, self.oldmaxx) = self.getScreenDimensions()
        self.mode = SELECT_MODE

        # lets loop through and split
        self.lineMatches = []

        for lineObj in self.lineObjs.values():
            lineObj.controller = self
            if not lineObj.isSimple():
                self.lineMatches.append(lineObj)

        self.numLines = len(lineObjs.keys())
        self.numMatches = len(self.lineMatches)

        # begin tracking dirty state
        self.resetDirty()

        self.setHover(self.hoverIndex, True)

        # the scroll offset might not start off
        # at 0 if our first real match is WAY
        # down the screen -- so lets init it to
        # a valid value after we have all our line objects
        self.updateScrollOffset()

        logger.addEvent('init')

    def getScrollOffset(self):
        return self.scrollOffset

    def getScreenDimensions(self):
        return self.stdscr.getmaxyx()

    def getChromeBoundaries(self):
        (maxy, maxx) = self.stdscr.getmaxyx()
        minx = CHROME_MIN_X if self.scrollBar.getIsActivated(
        ) or self.mode == X_MODE else 0
        maxy = self.helperChrome.reduceMaxY(maxy)
        maxx = self.helperChrome.reduceMaxX(maxx)
        # format of (MINX, MINY, MAXX, MAXY)
        return (minx, CHROME_MIN_Y, maxx, maxy)

    def getViewportHeight(self):
        (minx, miny, maxx, maxy) = self.getChromeBoundaries()
        return maxy - miny

    def setHover(self, index, val):
        self.lineMatches[index].setHover(val)

    def toggleSelect(self):
        self.lineMatches[self.hoverIndex].toggleSelect()

    def toggleSelectAll(self):
        paths = set()
        for line in self.lineMatches:
            if line.getPath() not in paths:
                paths.add(line.getPath())
                line.toggleSelect()

    def setSelect(self, val):
        self.lineMatches[self.hoverIndex].setSelect(val)

    def describeFile(self):
        self.helperChrome.outputDescription(self.lineMatches[self.hoverIndex])

    def control(self):
        # we start out by printing everything we need to
        self.printAll()
        self.resetDirty()
        self.moveCursor()
        while True:
            inKey = self.getKey()
            self.checkResize()
            self.processInput(inKey)
            self.processDirty()
            self.resetDirty()
            self.moveCursor()
            self.stdscr.refresh()

    def checkResize(self):
        (maxy, maxx) = self.getScreenDimensions()
        if (maxy is not self.oldmaxy or maxx is not self.oldmaxx):
            # we resized so print all!
            self.printAll()
            self.resetDirty()
            self.stdscr.refresh()
            logger.addEvent('resize')
        (self.oldmaxy, self.oldmaxx) = self.getScreenDimensions()

    def updateScrollOffset(self):
        """
          yay scrolling logic! we will start simple here
          and basically just center the viewport to current
          matched line
      """
        windowHeight = self.getViewportHeight()
        halfHeight = int(round(windowHeight / 2.0))

        # important, we need to get the real SCREEN position
        # of the hover index, not its index within our matches
        hovered = self.lineMatches[self.hoverIndex]
        desiredTopRow = hovered.getScreenIndex() - halfHeight

        oldOffset = self.scrollOffset
        desiredTopRow = max(desiredTopRow, 0)
        newOffset = -desiredTopRow
        # lets add in some leeway -- dont bother repositioning
        # if the old offset is within 1/2 of the window height
        # of our desired (unless we absolutely have to)
        if abs(newOffset -
               oldOffset) > halfHeight / 2 or self.hoverIndex + oldOffset < 0:
            # need to reassign now we have gone too far
            self.scrollOffset = newOffset
        if oldOffset is not self.scrollOffset:
            self.dirtyAll()

        # also update our scroll bar
        self.scrollBar.calcBoxFractions()

    def pageDown(self):
        pageHeight = (int)(self.getViewportHeight() * 0.5)
        self.moveIndex(pageHeight)

    def pageUp(self):
        pageHeight = (int)(self.getViewportHeight() * 0.5)
        self.moveIndex(-pageHeight)

    def moveIndex(self, delta):
        newIndex = (self.hoverIndex + delta) % self.numMatches
        self.jumpToIndex(newIndex)
        # also clear the description pane if necessary
        self.helperChrome.clearDescriptionPane()

    def jumpToIndex(self, newIndex):
        self.setHover(self.hoverIndex, False)
        self.hoverIndex = newIndex
        self.setHover(self.hoverIndex, True)
        self.updateScrollOffset()

    def processInput(self, key):
        if key == 'UP' or key == 'k':
            self.moveIndex(-1)
        elif key == 'DOWN' or key == 'j':
            self.moveIndex(1)
        elif key == 'x':
            self.toggleXMode()
        elif key == 'c':
            self.beginEnterCommand()
        elif key == ' ' or key == 'NPAGE':
            self.pageDown()
        elif key == 'b' or key == 'PPAGE':
            self.pageUp()
        elif key == 'g' or key == 'HOME':
            self.jumpToIndex(0)
        elif (key == 'G' and not self.mode == X_MODE) or key == 'END':
            self.jumpToIndex(self.numMatches - 1)
        elif key == 'd':
            self.describeFile()
        elif key == 'f':
            self.toggleSelect()
        elif key == 'F':
            self.toggleSelect()
            self.moveIndex(1)
        elif key == 'A' and not self.mode == X_MODE:
            self.toggleSelectAll()
        elif key == 'ENTER' and (not self.flags.getAllInput() or len(self.flags.getPresetCommand())):
            # it does not make sense to process an 'ENTER' keypress if we're in the allInput
            # mode and there is not a preset command.
            self.onEnter()
        elif key == 'q':
            output.outputNothing()
            # this will get the appropriate selection and save it to a file for reuse
            # before exiting the program
            self.getPathsToUse()
            self.cursesAPI.exit()
        elif self.mode == X_MODE and key in lbls:
            self.selectXMode(key)
        pass

    def getPathsToUse(self):
        # if we have selected paths, those, otherwise hovered
        toUse = self.getSelectedPaths()
        if not toUse:
            toUse = self.getHoveredPaths()

        # save the selection we are using
        if self.cursesAPI.allowFileOutput():
            output.outputSelection(toUse)
        return toUse

    def getSelectedPaths(self):
        return [lineObj for (index, lineObj) in enumerate(self.lineMatches)
                if lineObj.getSelected()]

    def getHoveredPaths(self):
        return [lineObj for (index, lineObj) in enumerate(self.lineMatches)
                if index == self.hoverIndex]

    def showAndGetCommand(self):
        pathObjs = self.getPathsToUse()
        paths = [pathObj.getPath() for pathObj in pathObjs]
        (maxy, maxx) = self.getScreenDimensions()

        # Alright this is a bit tricy -- for tall screens, we try to aim
        # the command prompt right at the middle of the screen so you dont
        # have to shift your eyes down or up a bunch
        beginHeight = int(round(maxy / 2) - len(paths) / 2.0)
        # but if you have a TON of paths, we are going to start printing
        # way off screen. in this case lets just slap the prompt
        # at the bottom so we can fit as much as possible.
        #
        # There could better option here to slowly increase the prompt
        # height to the bottom, but this is good enough for now...
        if beginHeight <= 1:
            beginHeight = maxy - 6

        borderLine = '=' * len(SHORT_COMMAND_PROMPT)
        promptLine = '.' * len(SHORT_COMMAND_PROMPT)
        # from helper chrome code
        maxPathLength = maxx - 5
        if self.helperChrome.getIsSidebarMode():
            # need to be shorter to not go into side bar
            maxPathLength = len(SHORT_COMMAND_PROMPT) + 18

        # first lets print all the paths
        startHeight = beginHeight - 1 - len(paths)
        try:
            self.colorPrinter.addstr(startHeight - 3, 0, borderLine)
            self.colorPrinter.addstr(startHeight - 2, 0, SHORT_PATHS_HEADER)
            self.colorPrinter.addstr(startHeight - 1, 0, borderLine)
        except curses.error:
            pass

        for index, path in enumerate(paths):
            try:
                self.colorPrinter.addstr(
                    startHeight + index,
                    0,
                    path[0:maxPathLength]
                )
            except curses.error:
                pass

        # first print prompt
        try:
            self.colorPrinter.addstr(beginHeight, 0, SHORT_COMMAND_PROMPT)
            self.colorPrinter.addstr(beginHeight + 1, 0, SHORT_COMMAND_PROMPT2)
        except curses.error:
            pass
        # then line to distinguish and prompt line
        try:
            self.colorPrinter.addstr(beginHeight - 1, 0, borderLine)
            self.colorPrinter.addstr(beginHeight + 2, 0, borderLine)
            self.colorPrinter.addstr(beginHeight + 3, 0, promptLine)
        except curses.error:
            pass

        self.stdscr.refresh()
        self.cursesAPI.echo()
        maxX = int(round(maxx - 1))

        command = self.stdscr.getstr(beginHeight + 3, 0, maxX)
        return command

    def beginEnterCommand(self):
        self.stdscr.erase()
        # first check if they are trying to enter command mode
        # but already have a command...
        if len(self.flags.getPresetCommand()):
            self.helperChrome.output(self.mode)
            (minX, minY, _, maxY) = self.getChromeBoundaries()
            yStart = (maxY + minY) / 2 - 3
            self.printProvidedCommandWarning(yStart, minX)
            self.stdscr.refresh()
            self.getKey()
            self.mode = SELECT_MODE
            self.dirtyAll()
            return

        self.mode = COMMAND_MODE
        self.helperChrome.output(self.mode)
        logger.addEvent('enter_command_mode')

        command = self.showAndGetCommand()
        if len(command) == 0:
            # go back to selection mode and repaint
            self.mode = SELECT_MODE
            self.cursesAPI.noecho()
            self.dirtyAll()
            logger.addEvent('exit_command_mode')
            return
        lineObjs = self.getPathsToUse()
        output.execComposedCommand(command, lineObjs)
        sys.exit(0)

    def onEnter(self):
        lineObjs = self.getPathsToUse()
        if not lineObjs:
            # nothing selected, assume we want hovered
            lineObjs = self.getHoveredPaths()
        logger.addEvent('selected_num_files', len(lineObjs))

        # commands passed from the command line get used immediately
        presetCommand = self.flags.getPresetCommand()
        if len(presetCommand) > 0:
            output.execComposedCommand(presetCommand, lineObjs)
        else:
            output.editFiles(lineObjs)

        sys.exit(0)

    def resetDirty(self):
        # reset all dirty state for our components
        self.dirty = False
        self.dirtyIndexes = []

    def dirtyLine(self, index):
        self.dirtyIndexes.append(index)

    def dirtyAll(self):
        self.dirty = True

    def processDirty(self):
        if self.dirty:
            self.printAll()
            return
        (minx, miny, maxx, maxy) = self.getChromeBoundaries()
        didClearLine = False
        for index in self.dirtyIndexes:
            y = miny + index + self.getScrollOffset()
            if y >= miny and y < maxy:
                didClearLine = True
                self.clearLine(y)
                self.lineObjs[index].output(self.colorPrinter)
        if didClearLine and self.helperChrome.getIsSidebarMode():
            # now we need to output the chrome again since on wide
            # monitors we will have cleared out a line of the chrome
            self.helperChrome.output(self.mode)

    def clearLine(self, y):
        '''Clear a line of content, excluding the chrome'''
        (minx, _, _, _) = self.getChromeBoundaries()
        (_, maxx) = self.stdscr.getmaxyx()
        charsToDelete = range(minx, maxx)
        # we go in the **reverse** order since the original documentation
        # of delchar (http://dell9.ma.utexas.edu/cgi-bin/man-cgi?delch+3)
        # mentions that delchar actually moves all the characters to the right
        # of the cursor
        for x in reversed(charsToDelete):
            self.stdscr.delch(y, x)

    def printAll(self):
        self.stdscr.erase()
        self.printLines()
        self.printScroll()
        self.printXMode()
        self.printChrome()

    def printLines(self):
        for lineObj in self.lineObjs.values():
            lineObj.output(self.colorPrinter)

    def printScroll(self):
        self.scrollBar.output()

    def printProvidedCommandWarning(self, yStart, xStart):
        self.colorPrinter.addstr(yStart, xStart, 'Oh no! You already provided a command so ' +
                                 'you cannot enter command mode.',
                                 self.colorPrinter.getAttributes(curses.COLOR_WHITE,
                                                                 curses.COLOR_RED,
                                                                 0))

        self.colorPrinter.addstr(
            yStart + 1, xStart, 'The command you provided was "%s" ' % self.flags.getPresetCommand())
        self.colorPrinter.addstr(
            yStart + 2, xStart, 'Press any key to go back to selecting paths.')

    def printChrome(self):
        self.helperChrome.output(self.mode)

    def moveCursor(self):
        x = CHROME_MIN_X if self.scrollBar.getIsActivated() else 0
        y = self.lineMatches[
            self.hoverIndex].getScreenIndex() + self.scrollOffset
        self.stdscr.move(y, x)

    def getKey(self):
        charCode = self.stdscr.getch()
        return CODE_TO_CHAR.get(charCode, '')

    def toggleXMode(self):
        self.mode = X_MODE if self.mode != X_MODE else SELECT_MODE
        self.printAll()

    def printXMode(self):
        if self.mode == X_MODE:
            (maxy, _) = self.scrollBar.screenControl.getScreenDimensions()
            topY = maxy - 2
            minY = self.scrollBar.getMinY() - 1
            for i in range(minY, topY + 1):
                idx = i - minY
                if idx < len(lbls):
                    self.colorPrinter.addstr(i, 1, lbls[idx])

    def selectXMode(self, key):
        lineObj = self.lineObjs[
            lbls.index(key) - self.scrollOffset]
        if type(lineObj) == format.LineMatch:
            lineMatchIndex = self.lineMatches.index(lineObj)
            self.hoverIndex = lineMatchIndex
            self.toggleSelect()
