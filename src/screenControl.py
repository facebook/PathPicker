# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint
import curses
import os
import sys
import signal

import processInput
import output

def signal_handler(signal, frame):
    # from http://stackoverflow.com/a/1112350/948126
    # Lets just quit rather than signal.SIGINT printing the stack
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

import logger

PICKLE_FILE = '~/.fbPager.pickle'
CHROME_MIN_X = 5
CHROME_MIN_Y = 0

mapping = {i: chr(i) for i in range(256)}
mapping.update((value, name[4:]) for name, value in vars(curses).items()
               if name.startswith('KEY_'))
# special exceptions
mapping[4] = 'PAGE_DOWN'
mapping[10] = 'ENTER'
mapping[21] = 'PAGE_UP'

SELECT_MODE = 'SELECT'
COMMAND_MODE = 'COMMAND_MODE'

SHORT_NAV_USAGE = '[f|A] selection, [down|j|up|k|space|b] navigation, [enter] open, [c] command mode'
SHORT_COMMAND_USAGE = 'command examples: | git add | git checkout HEAD~1 -- | mv $F ../here/ |'
SHORT_COMMAND_PROMPT = 'Type a command below! Files will be appended or replace $F'
SHORT_COMMAND_PROMPT2 = 'Enter a blank line to go back to the selection process'
SHORT_FILES_HEADER = 'Files you have selected:'

INVISIBLE_CURSOR = 0
BLOCK_CURSOR = 2


class HelperChrome(object):

    def __init__(self, stdscr, screenControl):
        self.stdscr = stdscr
        self.screenControl = screenControl
        self.WIDTH = 50
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

    def toggleCursor(self):
        if self.mode == SELECT_MODE:
            curses.curs_set(INVISIBLE_CURSOR)
        else:
            curses.curs_set(BLOCK_CURSOR)

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

    def outputSide(self):
        if not self.getIsSidebarMode():
            return
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        borderX = maxx - self.WIDTH
        if (self.mode == COMMAND_MODE):
            borderX = len(SHORT_COMMAND_PROMPT) + 20
        usageLines = processInput.USAGE_PAGE.split('\n')
        if self.mode == COMMAND_MODE:
            usageLines = processInput.USAGE_COMMAND.split('\n')
        for index, usageLine in enumerate(usageLines):
            self.stdscr.addstr(self.getMinY() + index, borderX + 2, usageLine)
        for y in range(self.getMinY(), maxy):
            self.stdscr.addstr(y, borderX, '|')

    def outputBottom(self):
        if self.getIsSidebarMode():
            return
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        borderY = maxy - 2
        # first output text since we might throw an exception during border
        usageStr = SHORT_NAV_USAGE if self.mode == SELECT_MODE else SHORT_COMMAND_USAGE
        borderStr = '_' * (maxx - self.getMinX() - 0)
        self.stdscr.addstr(borderY, self.getMinX(), borderStr)
        self.stdscr.addstr(borderY + 1, self.getMinX(), usageStr)


class ScrollBar(object):

    def __init__(self, stdscr, lines, screenControl):
        self.stdscr = stdscr
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
            self.stdscr.addstr(y, x, ' ')

    def outputBox(self):
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        topY = maxy - 2
        minY = self.getMinY()
        diff = topY - minY
        x = self.getX()

        boxStartY = int(diff * self.boxStartFraction) + minY
        boxStopY = int(diff * self.boxStopFraction) + minY

        self.stdscr.addstr(boxStartY, x, '/-\\')
        for y in range(boxStartY + 1, boxStopY):
            self.stdscr.addstr(y, x, '|-|')
        self.stdscr.addstr(boxStopY, x, '\-/')

    def outputCaps(self):
        x = self.getX()
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        for y in [self.getMinY() - 1, maxy - 1]:
            self.stdscr.addstr(y, x, '===')

    def outputBase(self):
        x = self.getX()
        (maxy, maxx) = self.screenControl.getScreenDimensions()
        for y in range(self.getMinY(), maxy - 1):
            self.stdscr.addstr(y, x, ' . ')


class Controller(object):

    def __init__(self, stdscr, lineObjs, keepOpen=False):
        self.stdscr = stdscr
        self.lineObjs = lineObjs
        self.hoverIndex = 0
        self.scrollOffset = 0
        self.scrollBar = ScrollBar(stdscr, lineObjs, self)
        self.helperChrome = HelperChrome(stdscr, self)
        (self.oldmaxy, self.oldmaxx) = self.getScreenDimensions()
        self.mode = SELECT_MODE
        self.keepOpen = keepOpen

        self.simpleLines = []
        self.lineMatches = []
        # lets loop through and split
        for key, lineObj in self.lineObjs.items():
            lineObj.setController(self)
            if (lineObj.isSimple()):
                self.simpleLines.append(lineObj)
            else:
                self.lineMatches.append(lineObj)

        self.numLines = len(lineObjs.keys())
        self.numMatches = len(self.lineMatches)

        self.setHover(self.hoverIndex, True)
        curses.use_default_colors()
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
        minx = CHROME_MIN_X if self.scrollBar.getIsActivated() else 0
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
        self.dirtyHoverIndex()
        self.lineMatches[self.hoverIndex].toggleSelect()

    def toggleSelectAll(self):
        files = set()
        for line in self.lineMatches:
            if line.getFile() not in files:
                files.add(line.getFile())
                line.toggleSelect()

        self.dirtyLines()

    def setSelect(self, val):
        self.lineMatches[self.hoverIndex].setSelect(val)

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
            self.dirtyLines()

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

    def jumpToIndex(self, newIndex):
        self.setHover(self.hoverIndex, False)
        self.dirtyHoverIndex()

        self.hoverIndex = newIndex
        self.setHover(self.hoverIndex, True)
        self.dirtyHoverIndex()
        self.updateScrollOffset()

    def processInput(self, key):
        if key == 'UP' or key == 'k':
            self.moveIndex(-1)
        elif key == 'DOWN' or key == 'j':
            self.moveIndex(1)
        elif key == 'c':
            self.beginEnterCommand()
        elif key == ' ' or key == 'PAGE_DOWN':
            self.pageDown()
        elif key == 'b' or key == 'PAGE_UP':
            self.pageUp()
        elif key == 'g':
            self.jumpToIndex(0)
        elif key == 'G':
            self.jumpToIndex(self.numMatches - 1)
        elif key == 'f':
            self.toggleSelect()
        elif key == 'A':
            self.toggleSelectAll()
        elif key == 'ENTER':
            self.onEnter()
        elif key == 'q':
            output.outputNothing()
            # this will get the appropriate selection and save it to a file for reuse
            # before exiting the program
            self.getFilesToUse()
            sys.exit(0)
        pass

    def getFilesToUse(self):
        # if we have select files, those, otherwise hovered
        toUse = self.getSelectedFiles()
        if not toUse:
            toUse = self.getHoveredFiles()

        # save the selection we are using
        output.outputSelection(toUse)
        return toUse

    def getSelectedFiles(self):
        return [lineObj for (index, lineObj) in enumerate(self.lineMatches)
                if lineObj.getSelected()]

    def getHoveredFiles(self):
        return [lineObj for (index, lineObj) in enumerate(self.lineMatches)
                if index == self.hoverIndex]

    def showAndGetCommand(self):
        fileObjs = self.getFilesToUse()
        files = [fileObj.getFile() for fileObj in fileObjs]
        (maxy, maxx) = self.getScreenDimensions()
        halfHeight = int(round(maxy / 2) - len(files) / 2.0)

        borderLine = '=' * len(SHORT_COMMAND_PROMPT)
        promptLine = '.' * len(SHORT_COMMAND_PROMPT)
        # from helper chrome code
        maxFileLength = maxx - 5
        if self.helperChrome.getIsSidebarMode():
            # need to be shorter to not go into side bar
            maxFileLength = len(SHORT_COMMAND_PROMPT) + 18

        # first lets print all the files
        startHeight = halfHeight - 1 - len(files)
        try:
            self.stdscr.addstr(startHeight - 3, 0, borderLine)
            self.stdscr.addstr(startHeight - 2, 0, SHORT_FILES_HEADER)
            self.stdscr.addstr(startHeight - 1, 0, borderLine)
            for index, file in enumerate(files):
                self.stdscr.addstr(startHeight + index, 0,
                                   file[0:maxFileLength])
        except curses.error:
            pass

        # first print prompt
        try:
            self.stdscr.addstr(halfHeight, 0, SHORT_COMMAND_PROMPT)
            self.stdscr.addstr(halfHeight + 1, 0, SHORT_COMMAND_PROMPT2)
        except curses.error:
            pass
        # then line to distinguish and prompt line
        try:
            self.stdscr.addstr(halfHeight - 1, 0, borderLine)
            self.stdscr.addstr(halfHeight + 2, 0, borderLine)
            self.stdscr.addstr(halfHeight + 3, 0, promptLine)
        except curses.error:
            pass

        self.stdscr.refresh()
        curses.echo()
        maxX = int(round(maxx - 1))
        command = self.stdscr.getstr(halfHeight + 3, 0, maxX)
        return command

    def beginEnterCommand(self):
        self.stdscr.clear()
        self.mode = COMMAND_MODE
        self.helperChrome.output(self.mode)
        logger.addEvent('enter_command_mode')

        command = self.showAndGetCommand()
        if len(command) == 0:
            # go back to selection mode and repaint
            self.mode = SELECT_MODE
            curses.noecho()
            self.dirtyLines()
            logger.addEvent('exit_command_mode')
            return
        lineObjs = self.getFilesToUse()
        output.execComposedCommand(command, lineObjs)
        sys.run()

    def onEnter(self):
        lineObjs = self.getFilesToUse()
        if not lineObjs:
            # nothing selected, assume we want hovered
            lineObjs = self.getHoveredFiles()
        logger.addEvent('selected_num_files', len(lineObjs))
        output.editFiles(lineObjs)
        self.run()

    def run(self):
        if self.keepOpen:
            os.system('sh ~/.fbPager.sh; rm -f ~/.fbPager.sh')
            self.dirtyLines()
            self.processDirty()
        else:
            sys.exit(0)

    def resetDirty(self):
        # reset all dirty state for our components
        self.linesDirty = False
        self.dirtyIndexes = []

    def dirtyHoverIndex(self):
        self.dirtyIndexes.append(self.hoverIndex)

    def dirtyLines(self):
        self.linesDirty = True

    def processDirty(self):
        if self.linesDirty:
            self.printAll()
        for index in self.dirtyIndexes:
            self.lineMatches[index].output(self.stdscr)
        if self.helperChrome.getIsSidebarMode():
            # need to output since lines can override
            # the sidebar stuff
            self.printChrome()

    def printAll(self):
        self.stdscr.clear()
        self.printLines()
        self.printScroll()
        self.printChrome()

    def printLines(self):
        for key, lineObj in self.lineObjs.items():
            lineObj.output(self.stdscr)

    def printScroll(self):
        self.scrollBar.output()

    def printChrome(self):
        self.helperChrome.output(self.mode)

    def moveCursor(self):
        x = CHROME_MIN_X if self.scrollBar.getIsActivated() else 0
        y = self.lineMatches[
            self.hoverIndex].getScreenIndex() + self.scrollOffset
        self.stdscr.move(y, x)

    def getKey(self):
        charCode = self.stdscr.getch()
        return mapping.get(charCode, '')
