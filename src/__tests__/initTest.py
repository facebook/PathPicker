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
sys.path.insert(0,'../')

import choose
import processInput
from screenForTest import ScreenForTest
from cursesForTest import CursesForTest

def getLineObjsFromFile(inputFile):
    lines = open(inputFile).read().split('\n')
    return processInput.getLineObjsFromLines(lines)

def initScreenTest(inputFile='./inputs/gitDiff.txt', charInputs=['q']):
    lineObjs = getLineObjsFromFile(inputFile)
    screen = ScreenForTest(charInputs)
    try:
        choose.doProgram(screen, CursesForTest(), lineObjs)
    except StopIteration:
        screen.printScreen()

if __name__ == '__main__':
    initScreenTest()
