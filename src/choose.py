# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import curses
import pickle
import sys
import os

import output
import screenControl
import logger
import format
import stateFiles
from cursesAPI import CursesAPI
from screenFlags import ScreenFlags

LOAD_SELECTION_WARNING = '''
WARNING! Loading the standard input and previous selection
failed. This is probably due to a backwards compatibility issue
with upgrading PathPicker or an internal error. Please pipe
a new set of input to PathPicker to start fresh (after which
this error will go away)
'''


def doProgram(stdscr, flags, cursesAPI=None, lineObjs=None):
    # curses and lineObjs get dependency injected for
    # our tests, so init these if they are not provided
    if not cursesAPI:
        cursesAPI = CursesAPI()
    if not lineObjs:
        lineObjs = getLineObjs()
    output.clearFile()
    logger.clearFile()
    screen = screenControl.Controller(flags, stdscr, lineObjs, cursesAPI)
    screen.control()


def getLineObjs():
    filePath = stateFiles.getPickleFilePath()
    try:
        lineObjs = pickle.load(open(filePath, 'rb'))
    except:
        output.appendError(LOAD_SELECTION_WARNING)
        output.appendExit()
        sys.exit(1)
    logger.addEvent('total_num_files', len(lineObjs))

    selectionPath = stateFiles.getSelectionFilePath()
    if os.path.isfile(selectionPath):
        setSelectionsFromPickle(selectionPath, lineObjs)

    matches = [lineObj for lineObj in lineObjs.values()
               if not lineObj.isSimple()]
    if not len(matches):
        output.writeToFile('echo "No lines matched!!";')
        output.appendExit()
        sys.exit(0)
    return lineObjs


def setSelectionsFromPickle(selectionPath, lineObjs):
    try:
        selectedIndices = pickle.load(open(selectionPath, 'rb'))
    except:
        output.appendError(LOAD_SELECTION_WARNING)
        output.appendExit()
        sys.exit(1)
    for index in selectedIndices:
        if index >= len(lineObjs.items()):
            error = 'Found index %d more than total matches' % index
            output.appendError(error)
            continue
        toSelect = lineObjs[index]
        if isinstance(toSelect, format.LineMatch):
            lineObjs[index].setSelect(True)
        else:
            error = 'Line %d was selected but is not LineMatch' % index
            output.appendError(error)


if __name__ == '__main__':
    filePath = stateFiles.getPickleFilePath()
    if not os.path.exists(filePath):
        print('Nothing to do!')
        output.writeToFile('echo ":D";')
        output.appendExit()
        sys.exit(0)
    output.clearFile()
    # we initialize our args *before* we move into curses
    # so we can benefit from the default argparse
    # behavior:
    flags = ScreenFlags.initFromArgs(sys.argv[1:])
    curses.wrapper(lambda x: doProgram(x, flags))
