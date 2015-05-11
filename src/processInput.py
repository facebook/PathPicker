# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
import os
import pickle
import re

import parse
import format
import stateFiles
from formattedText import FormattedText
from usageStrings import USAGE_STR


def getLineObjs():
    inputLines = sys.stdin.readlines()
    lineObjs = {}
    for index, line in enumerate(inputLines):
        line = line.replace('\t', '    ')
        formattedLine = FormattedText(line)
        result = parse.matchLine(str(formattedLine))

        if not result:
            line = format.SimpleLine(formattedLine, index)
        else:
            line = format.LineMatch(formattedLine, result, index)

        lineObjs[index] = line

    return lineObjs


def doProgram():
    filePath = stateFiles.getPickleFilePath()
    lineObjs = getLineObjs()
    # pickle it so the next program can parse it
    pickle.dump(lineObjs, open(filePath, 'wb'))


def usage():
    print(USAGE_STR)


if __name__ == '__main__':
    if sys.stdin.isatty():
        if os.path.isfile(stateFiles.getPickleFilePath()):
            print('Using old result...')
        else:
            usage()
        # let the next stage parse the old version
        sys.exit(0)
    else:
        # delete the old selection
        print('getting input')
        selectionPath = stateFiles.getSelectionFilePath()
        if os.path.isfile(selectionPath):
            os.remove(selectionPath)

        doProgram()
        sys.exit(0)
