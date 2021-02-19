# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import pickle
import sys

from pathpicker import parse, state_files
from pathpicker.formatted_text import FormattedText
from pathpicker.line_format import LineMatch, SimpleLine
from pathpicker.screen_flags import ScreenFlags
from pathpicker.usage_strings import USAGE_STR


def getLineObjs(flags):
    inputLines = sys.stdin.readlines()
    return getLineObjsFromLines(
        inputLines,
        validateFileExists=not flags.get_disable_file_checks(),
        allInput=flags.get_all_input(),
    )


def getLineObjsFromLines(inputLines, validateFileExists=True, allInput=False):
    lineObjs = {}
    for index, line in enumerate(inputLines):
        line = line.replace("\t", "    ")
        # remove the new line as we place the cursor ourselves for each
        # line. this avoids curses errors when we newline past the end of the
        # screen
        line = line.replace("\n", "")
        formattedLine = FormattedText(line)
        result = parse.match_line(
            str(formattedLine),
            validate_file_exists=validateFileExists,
            all_input=allInput,
        )

        if not result:
            line = SimpleLine(formattedLine, index)
        else:
            line = LineMatch(
                formattedLine,
                result,
                index,
                validateFileExists=validateFileExists,
                allInput=allInput,
            )

        lineObjs[index] = line

    return lineObjs


def doProgram(flags):
    filePath = state_files.getPickleFilePath()
    lineObjs = getLineObjs(flags)
    # pickle it so the next program can parse it
    pickle.dump(lineObjs, open(filePath, "wb"))


def usage():
    print(USAGE_STR)


def main(argv) -> int:
    flags = ScreenFlags.init_from_args(argv[1:])
    if flags.get_is_clean_mode():
        print("Cleaning out state files...")
        for filePath in state_files.getAllStateFiles():
            if os.path.isfile(filePath):
                os.remove(filePath)
        print("Done! Removed %d files " % len(state_files.getAllStateFiles()))
        return 0
    if sys.stdin.isatty():
        if os.path.isfile(state_files.getPickleFilePath()):
            print("Using previous input piped to fpp...")
        else:
            usage()
        # let the next stage parse the old version
    else:
        # delete the old selection
        selection_path = state_files.getSelectionFilePath()
        if os.path.isfile(selection_path):
            os.remove(selection_path)
        doProgram(flags)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
