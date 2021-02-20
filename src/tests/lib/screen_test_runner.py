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


def get_line_objs_from_file(input_file, validate_file_exists, all_input):
    input_file = os.path.join(INPUT_DIR, input_file)
    file = open(input_file)
    lines = file.read().split("\n")
    file.close()
    return process_input.get_line_objs_from_lines(
        lines, validate_file_exists=validate_file_exists, all_input=all_input
    )


def get_rows_from_screen_run(
    input_file,
    char_inputs,
    screen_config=None,
    print_screen=True,
    past_screen=None,
    past_screens=None,
    validate_file_exists=False,
    all_input=False,
    args=None,
):
    if screen_config is None:
        screen_config = {}
    if args is None:
        args = []
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
