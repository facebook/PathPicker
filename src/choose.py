# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import os
import pickle
import sys
from typing import Optional

from pathpicker import logger, output, screen_control, state_files
from pathpicker.curses_api import CursesAPI
from pathpicker.key_bindings import KeyBindings, read_key_bindings
from pathpicker.line_format import LineMatch
from pathpicker.screen_flags import ScreenFlags

LOAD_SELECTION_WARNING = """
WARNING! Loading the standard input and previous selection
failed. This is probably due to a backwards compatibility issue
with upgrading PathPicker or an internal error. Please pipe
a new set of input to PathPicker to start fresh (after which
this error will go away)
"""


def doProgram(
    stdscr,
    flags,
    keyBindings: Optional[KeyBindings] = None,
    cursesAPI=None,
    lineObjs=None,
) -> None:
    # curses and lineObjs get dependency injected for
    # our tests, so init these if they are not provided
    if not keyBindings:
        keyBindings = read_key_bindings()
    if not cursesAPI:
        cursesAPI = CursesAPI()
    if not lineObjs:
        lineObjs = getLineObjs()
    output.clear_file()
    logger.clearFile()
    screen = screen_control.Controller(flags, keyBindings, stdscr, lineObjs, cursesAPI)
    screen.control()


def getLineObjs():
    filePath = state_files.getPickleFilePath()
    try:
        lineObjs = pickle.load(open(filePath, "rb"))
    except (OSError, KeyError, pickle.PickleError):
        output.append_error(LOAD_SELECTION_WARNING)
        output.append_exit()
        sys.exit(1)
    logger.addEvent("total_num_files", len(lineObjs))

    selectionPath = state_files.getSelectionFilePath()
    if os.path.isfile(selectionPath):
        setSelectionsFromPickle(selectionPath, lineObjs)

    matches = [lineObj for lineObj in lineObjs.values() if not lineObj.isSimple()]
    if not matches:
        output.write_to_file('echo "No lines matched!";')
        output.append_exit()
        sys.exit(0)
    return lineObjs


def setSelectionsFromPickle(selectionPath, lineObjs):
    try:
        selectedIndices = pickle.load(open(selectionPath, "rb"))
    except (OSError, KeyError, pickle.PickleError):
        output.append_error(LOAD_SELECTION_WARNING)
        output.append_exit()
        sys.exit(1)
    for index in selectedIndices:
        if index >= len(lineObjs.items()):
            error = "Found index %d more than total matches" % index
            output.append_error(error)
            continue
        toSelect = lineObjs[index]
        if isinstance(toSelect, LineMatch):
            lineObjs[index].setSelect(True)
        else:
            error = "Line %d was selected but is not LineMatch" % index
            output.append_error(error)


def main(argv) -> int:
    file_path = state_files.getPickleFilePath()
    if not os.path.exists(file_path):
        print("Nothing to do!")
        output.write_to_file('echo ":D";')
        output.append_exit()
        return 0
    output.clear_file()
    # we initialize our args *before* we move into curses
    # so we can benefit from the default argparse
    # behavior:
    flags = ScreenFlags.init_from_args(argv[1:])
    curses.wrapper(lambda x: doProgram(x, flags))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
