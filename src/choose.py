# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint
import curses
import pickle
import sys
import os
import output
import screenControl
import logger

PICKLE_FILE = '~/.fbPager.pickle'
SELECTION_PICKLE = '~/.fbPager.selection.pickle'


def doProgram(stdscr):
    output.clearFile()
    logger.clearFile()
    lineObjs = getLineObjs()
    screen = screenControl.Controller(stdscr, lineObjs)
    screen.control()


def getLineObjs():
    filePath = os.path.expanduser(PICKLE_FILE)
    lineObjs = pickle.load(open(filePath))
    matches = [lineObj for i, lineObj in lineObjs.items()
               if not lineObj.isSimple()]
    logger.addEvent('total_num_files', len(lineObjs.items()))

    selectionPath = os.path.expanduser(SELECTION_PICKLE)
    if os.path.isfile(selectionPath):
        selectedIndices = pickle.load(open(selectionPath))
        for index in selectedIndices:
            if index < len(matches):
                matches[index].setSelect(True)

    if not len(matches):
        output.writeToFile('echo "No lines matched!!"')
        sys.exit(0)
    return lineObjs


if __name__ == '__main__':
    if not os.path.exists(os.path.expanduser(PICKLE_FILE)):
        print 'Nothing to do!'
        output.writeToFile('echo ":D"')
        sys.exit(0)
    output.clearFile()
    curses.wrapper(doProgram)
