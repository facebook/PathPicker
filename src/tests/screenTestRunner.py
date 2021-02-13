# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import sys
import os

from tests.keyBindingsForTest import KeyBindingsForTest
from tests.cursesForTest import CursesForTest
from tests.screenForTest import ScreenForTest
from pathpicker.screenFlags import ScreenFlags
import processInput
import choose

INPUT_DIR = "./inputs/"


def getLineObjsFromFile(inputFile, validateFileExists, allInput):
    inputFile = os.path.join(INPUT_DIR, inputFile)
    file = open(inputFile)
    lines = file.read().split("\n")
    file.close()
    return processInput.getLineObjsFromLines(
        lines, validateFileExists=validateFileExists, allInput=allInput
    )


def getRowsFromScreenRun(
    inputFile,
    charInputs,
    screenConfig={},
    printScreen=True,
    pastScreen=None,
    pastScreens=None,
    validateFileExists=False,
    allInput=False,
    args=[],
):

    lineObjs = getLineObjsFromFile(
        inputFile, validateFileExists=validateFileExists, allInput=allInput
    )
    screen = ScreenForTest(
        charInputs,
        maxX=screenConfig.get("maxX", 80),
        maxY=screenConfig.get("maxY", 30),
    )

    # mock our flags with the passed arg list
    flags = ScreenFlags.initFromArgs(args)
    # we run our program and throw a StopIteration exception
    # instead of sys.exit-ing
    try:
        choose.doProgram(screen, flags, KeyBindingsForTest(), CursesForTest(), lineObjs)
    except StopIteration:
        pass

    if printScreen:
        screen.printOldScreens()

    if pastScreen:
        return screen.getRowsWithAttributesForPastScreen(pastScreen)
    elif pastScreens:
        return screen.getRowsWithAttributesForPastScreens(pastScreens)

    return screen.getRowsWithAttributes()
