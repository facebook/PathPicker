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

EXPECTED_DIR = './expected/'

def getLineObjsFromFile(inputFile):
    lines = open(inputFile).read().split('\n')
    return processInput.getLineObjsFromLines(lines)

def compareToExpected(testName, actualLines):
    expectedFile = os.path.join(EXPECTED_DIR, testName + '.txt')
    if not os.path.isdir(EXPECTED_DIR):
        os.makedirs(EXPECTED_DIR)
    if not os.path.isfile(expectedFile):
        print('Could not find file %s so outputting...' % expectedFile)
        file = open(expectedFile, 'w')
        file.write('\n'.join(actualLines))
        file.close()
        print('File outputted, please inspect for correctness')
        return
    expectedLines = open(expectedFile).read().split('\n')
    if len(actualLines) != len(expectedLines):
        print('error!! not equal %d %d' % (len(actualLines), len(expectedLines)))
    for index, expectedLine in enumerate(expectedLines):
        actualLine = actualLines[index]
        if expectedLine == actualLine:
            print('it is correct! %s ' % expectedLine)
        else:
            print('%s and %s did not match ' % (expectedLine, actualLine))

def initScreenTest(inputFile, charInputs, testName):
    lineObjs = getLineObjsFromFile(inputFile)
    screen = ScreenForTest(charInputs)
    try:
        choose.doProgram(screen, CursesForTest(), lineObjs)
    except StopIteration:
        pass
    screen.printScreen()
    compareToExpected(testName, screen.getRows())

if __name__ == '__main__':
    initScreenTest(
        inputFile='./inputs/gitDiff.txt',
        charInputs=['q'],
        testName='simpleGitDiff',
    )
