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
import os

sys.path.insert(0, '../')

import choose
import processInput
from screenFlags import ScreenFlags

from screenForTest import ScreenForTest
from cursesForTest import CursesForTest

INPUT_DIR = './inputs/'


def getLineObjsFromFile(inputFile):
    inputFile = os.path.join(INPUT_DIR, inputFile)
    file = open(inputFile)
    lines = file.read().split('\n')
    file.close()
    return processInput.getLineObjsFromLines(lines)


def getRowsFromScreenRun(
        inputFile,
        charInputs,
        screenConfig={},
        printScreen=True,
        pastScreen=None,
        args=[]):

    lineObjs = getLineObjsFromFile(inputFile)
    screen = ScreenForTest(
        charInputs,
        maxX=screenConfig.get('maxX', 80),
        maxY=screenConfig.get('maxY', 30),
    )
    # mock our flags with thep assed arg list
    flags = ScreenFlags.initFromArgs(args)
    try:
        choose.doProgram(screen, flags, CursesForTest(), lineObjs)
    except StopIteration:
        pass
    if printScreen:
        screen.printOldScreens()
    if pastScreen:
        return screen.getRowsForPastScreen(pastScreen)
    return screen.getRows()

if __name__ == '__main__':
    getRowsFromScreenRun(
        inputFile='gitDiff.txt',
        charInputs=['q'],
    )
