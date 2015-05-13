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
sys.path.insert(0,'../')

import choose
import processInput
from screenForTest import ScreenForTest
from cursesForTest import CursesForTest

INPUT_DIR = './inputs/'

def getLineObjsFromFile(inputFile):
    inputFile = os.path.join(INPUT_DIR, inputFile)
    lines = open(inputFile).read().split('\n')
    return processInput.getLineObjsFromLines(lines)

def getRowsFromScreenRun(inputFile, charInputs, printScreen=True):
    lineObjs = getLineObjsFromFile(inputFile)
    screen = ScreenForTest(charInputs)
    try:
        choose.doProgram(screen, CursesForTest(), lineObjs)
    except StopIteration:
        pass
    if printScreen:
        screen.printScreen()
    return screen.getRows()

if __name__ == '__main__':
    getRowsFromScreenRun(
        inputFile='gitDiff.txt',
        charInputs=['q'],
    )
