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
    return process_input.get_line_objs_from_lines(
        lines, validate_file_exists=validateFileExists, all_input=allInput
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
        max_x=screenConfig.get("maxX", 80),
        max_y=screenConfig.get("maxY", 30),
    )

    # mock our flags with the passed arg list
    flags = ScreenFlags.init_from_args(args)
    # we run our program and throw a StopIteration exception
    # instead of sys.exit-ing
    try:
        choose.do_program(
            screen, flags, KEY_BINDINGS_FOR_TEST, CursesForTest(), lineObjs
        )
    except StopIteration:
        pass

    if printScreen:
        screen.print_old_screens()

    if pastScreen:
        return screen.get_rows_with_attributes_for_past_screen(pastScreen)
    if pastScreens:
        return screen.get_rows_with_attributes_for_past_screens(pastScreens)
    return screen.get_rows_with_attributes()
