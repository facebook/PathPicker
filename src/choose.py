# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import os
import pickle
import sys
from typing import List, Optional

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


def do_program(
    stdscr,
    flags: ScreenFlags,
    key_bindings: Optional[KeyBindings] = None,
    curses_api=None,
    line_objs=None,
) -> None:
    # curses and lineObjs get dependency injected for
    # our tests, so init these if they are not provided
    if not key_bindings:
        key_bindings = read_key_bindings()
    if not curses_api:
        curses_api = CursesAPI()
    if not line_objs:
        line_objs = get_line_objs()
    output.clear_file()
    logger.clear_file()
    screen = screen_control.Controller(
        flags, key_bindings, stdscr, line_objs, curses_api
    )
    screen.control()


def get_line_objs():
    file_path = state_files.get_pickle_file_path()
    try:
        line_objs = pickle.load(open(file_path, "rb"))
    except (OSError, KeyError, pickle.PickleError):
        output.append_error(LOAD_SELECTION_WARNING)
        output.append_exit()
        sys.exit(1)
    logger.add_event("total_num_files", len(line_objs))

    selection_path = state_files.get_selection_file_path()
    if os.path.isfile(selection_path):
        set_selections_from_pickle(selection_path, line_objs)

    matches = [line_obj for line_obj in line_objs.values() if not line_obj.is_simple()]
    if not matches:
        output.write_to_file('echo "No lines matched!";')
        output.append_exit()
        sys.exit(0)
    return line_objs


def set_selections_from_pickle(selection_path, line_objs) -> None:
    try:
        selected_indices = pickle.load(open(selection_path, "rb"))
    except (OSError, KeyError, pickle.PickleError):
        output.append_error(LOAD_SELECTION_WARNING)
        output.append_exit()
        sys.exit(1)
    for index in selected_indices:
        if index >= len(line_objs.items()):
            error = "Found index %d more than total matches" % index
            output.append_error(error)
            continue
        to_select = line_objs[index]
        if isinstance(to_select, LineMatch):
            line_objs[index].set_select(True)
        else:
            error = "Line %d was selected but is not LineMatch" % index
            output.append_error(error)


def main(argv: List[str]) -> int:
    file_path = state_files.get_pickle_file_path()
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
    curses.wrapper(lambda x: do_program(x, flags))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
