# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Dict, List, Optional, Tuple

import choose
import process_input
from pathpicker.line_format import LineBase
from pathpicker.screen_flags import ScreenFlags
from tests.lib.curses_api import CursesForTest
from tests.lib.key_bindings import KEY_BINDINGS_FOR_TEST
from tests.lib.screen import ScreenForTest

INPUT_DIR = "./inputs/"


def get_line_objs_from_file(
    input_file: str, validate_file_exists: bool, all_input: bool
) -> Dict[int, LineBase]:
    input_file = os.path.join(INPUT_DIR, input_file)
    file = open(input_file)
    lines = file.read().split("\n")
    file.close()
    return process_input.get_line_objs_from_lines(
        lines, validate_file_exists=validate_file_exists, all_input=all_input
    )


def get_rows_from_screen_run(
    input_file: str,
    char_inputs: List[str],
    screen_config: Dict[str, int],
    print_screen: bool,
    past_screen: Optional[int],
    past_screens: Optional[List[int]],
    args: List[str],
    validate_file_exists: bool,
    all_input: bool,
) -> Tuple[List[str], List[str]]:
    line_objs = get_line_objs_from_file(
        input_file, validate_file_exists=validate_file_exists, all_input=all_input
    )
    screen = ScreenForTest(
        char_inputs,
        max_x=screen_config.get("maxX", 80),
        max_y=screen_config.get("maxY", 30),
    )

    # mock our flags with the passed arg list
    flags = ScreenFlags.init_from_args(args)
    # we run our program and throw a StopIteration exception
    # instead of sys.exit-ing
    try:
        choose.do_program(
            screen, flags, KEY_BINDINGS_FOR_TEST, CursesForTest(), line_objs
        )
    except StopIteration:
        pass

    if print_screen:
        screen.print_old_screens()

    if past_screen:
        return screen.get_rows_with_attributes_for_past_screen(past_screen)
    if past_screens:
        return screen.get_rows_with_attributes_for_past_screens(past_screens)
    return screen.get_rows_with_attributes()
