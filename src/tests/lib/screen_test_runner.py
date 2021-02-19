# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os

import choose
import process_input
from pathpicker.screen_flags import ScreenFlags
from tests.lib.curses import CursesForTest
from tests.lib.key_bindings import KEY_BINDINGS_FOR_TEST
from tests.lib.screen import ScreenForTest

INPUT_DIR = "./inputs/"


def getLineObjsFromFile(inputFile, validateFileExists, allInput):
    inputFile = os.path.join(INPUT_DIR, inputFile)
    file = open(inputFile)
    lines = file.read().split("\n")
    file.close()
    return process_input.getLineObjsFromLines(
        lines, validateFileExists=validateFileExists, allInput=allInput
    )


def getRowsFromScreenRun(
    inputFile,
    charInputs,
    screenConfig=None,
    printScreen=True,
    pastScreen=None,
    pastScreens=None,
    validateFileExists=False,
    allInput=False,
    args=None,
):
    if screenConfig is None:
        screenConfig = {}
    if args is None:
        args = []
    lineObjs = getLineObjsFromFile(
        inputFile, validateFileExists=validateFileExists, allInput=allInput
    )
    screen = ScreenForTest(
        charInputs,
        maxX=screenConfig.get("maxX", 80),
        maxY=screenConfig.get("maxY", 30),
    )

    # mock our flags with the passed arg list
    flags = ScreenFlags.init_from_args(args)
    # we run our program and throw a StopIteration exception
    # instead of sys.exit-ing
    try:
        choose.doProgram(
            screen, flags, KEY_BINDINGS_FOR_TEST, CursesForTest(), lineObjs
        )
    except StopIteration:
        pass

    if printScreen:
        screen.printOldScreens()

    if pastScreen:
        return screen.getRowsWithAttributesForPastScreen(pastScreen)
    if pastScreens:
        return screen.getRowsWithAttributesForPastScreens(pastScreens)
    return screen.getRowsWithAttributes()
