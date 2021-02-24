# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import pickle
import sys
from typing import Dict, List

from pathpicker import parse, state_files
from pathpicker.formatted_text import FormattedText
from pathpicker.line_format import LineBase, LineMatch, SimpleLine
from pathpicker.screen_flags import ScreenFlags
from pathpicker.usage_strings import USAGE_STR


def get_line_objs(flags: ScreenFlags) -> Dict[int, LineBase]:
    input_lines = sys.stdin.readlines()
    return get_line_objs_from_lines(
        input_lines,
        validate_file_exists=not flags.get_disable_file_checks(),
        all_input=flags.get_all_input(),
    )


def get_line_objs_from_lines(
    input_lines: List[str], validate_file_exists: bool = True, all_input: bool = False
) -> Dict[int, LineBase]:
    line_objs: Dict[int, LineBase] = {}
    for index, line in enumerate(input_lines):
        line = line.replace("\t", " " * 4)
        # remove the new line as we place the cursor ourselves for each
        # line. this avoids curses errors when we newline past the end of the
        # screen
        line = line.replace("\n", "")
        formatted_line = FormattedText(line)
        result = parse.match_line(
            str(formatted_line),
            validate_file_exists=validate_file_exists,
            all_input=all_input,
        )

        if not result:
            line_obj: LineBase = SimpleLine(formatted_line, index)
        else:
            line_obj = LineMatch(
                formatted_line,
                result,
                index,
                validate_file_exists=validate_file_exists,
                all_input=all_input,
            )

        line_objs[index] = line_obj

    return line_objs


def do_program(flags: ScreenFlags) -> None:
    file_path = state_files.get_pickle_file_path()
    line_objs = get_line_objs(flags)
    # pickle it so the next program can parse it
    pickle.dump(line_objs, open(file_path, "wb"))


def usage() -> None:
    print(USAGE_STR)


def main(argv: List[str]) -> int:
    flags = ScreenFlags.init_from_args(argv[1:])
    if flags.get_is_clean_mode():
        print("Cleaning out state files...")
        for file_path in state_files.get_all_state_files():
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"Done! Removed {len(state_files.get_all_state_files())} files ")
        return 0
    if sys.stdin.isatty():
        # don't keep the old selection if the --keep-open option is used;
        # otherwise you need to manually clear the old selection every
        # time fpp is reopened.
        if flags.get_keep_open():
            # delete the old selection
            selection_path = state_files.get_selection_file_path()
            if os.path.isfile(selection_path):
                os.remove(selection_path)
        if os.path.isfile(state_files.get_pickle_file_path()):
            print("Using previous input piped to fpp...")
        else:
            usage()
        # let the next stage parse the old version
    else:
        # delete the old selection
        selection_path = state_files.get_selection_file_path()
        if os.path.isfile(selection_path):
            os.remove(selection_path)
        do_program(flags)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
