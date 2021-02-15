# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import re
import sys
import unittest
from typing import Dict, List, Optional

from tests.lib import screen_test_runner

EXPECTED_DIR = "./expected/"


class ScreenTestCase:
    def __init__(
        self,
        name: str,
        input_file: str = "gitDiff.txt",
        inputs: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        screen_config: Optional[Dict[str, int]] = None,
        past_screen: Optional[int] = None,
        past_screens: Optional[List[int]] = None,
        with_attributes: bool = False,
        validate_file_exists: bool = False,
    ):
        self.name = name
        self.input_file = input_file
        self.inputs = inputs if inputs is not None else []
        self.args = args if args is not None else []
        self.screen_config = screen_config if screen_config is not None else {}
        self.past_screen = past_screen
        self.past_screens = past_screens
        self.with_attributes = with_attributes
        self.validate_file_exists = validate_file_exists


SCREEN_TEST_CASES: List[ScreenTestCase] = [
    ScreenTestCase("simpleLoadAndQuit"),
    ScreenTestCase(
        "tallLoadAndQuit",
        screen_config={
            "maxX": 140,
            "maxY": 60,
        },
    ),
    ScreenTestCase("selectFirst", inputs=["f"]),
    ScreenTestCase("selectFirstWithDown", inputs=["F"]),
    ScreenTestCase("selectDownSelect", inputs=["f", "j", "f"]),
    ScreenTestCase("selectWithDownSelect", inputs=["F", "f"]),
    ScreenTestCase("selectDownSelectInverse", inputs=["f", "j", "f", "A"]),
    ScreenTestCase("selectWithDownSelectInverse", inputs=["F", "F", "A"]),
    ScreenTestCase(
        "selectTwoCommandMode",
        input_file="absoluteGitDiff.txt",
        inputs=["f", "j", "f", "c"],
        past_screen=3,
    ),
    ScreenTestCase("selectAllFromArg", input_file="absoluteGitDiff.txt", args=["-a"]),
    ScreenTestCase("executeKeysEndKeySelectLast", args=["-e", "END", "f"]),
    # the last key "a" is so we quit from command mode
    # after seeing the warning
    ScreenTestCase(
        "selectCommandWithPassedCommand",
        input_file="absoluteGitDiff.txt",
        with_attributes=True,
        inputs=["f", "c", "a"],
        past_screen=1,
        args=["-c 'git add'"],
    ),
    ScreenTestCase("simpleWithAttributes", with_attributes=True),
    ScreenTestCase(
        "simpleSelectWithAttributes", with_attributes=True, inputs=["f", "j"]
    ),
    ScreenTestCase(
        "simpleSelectWithColor",
        input_file="gitDiffColor.txt",
        with_attributes=True,
        inputs=["f", "j"],
        screen_config={
            "maxX": 200,
            "maxY": 40,
        },
    ),
    ScreenTestCase(
        "gitDiffWithScroll", input_file="gitDiffNoStat.txt", inputs=["f", "j"]
    ),
    ScreenTestCase(
        "gitDiffWithScrollUp", input_file="gitLongDiff.txt", inputs=["k", "k"]
    ),
    ScreenTestCase(
        "gitDiffWithPageDown", input_file="gitLongDiff.txt", inputs=[" ", " "]
    ),
    ScreenTestCase(
        "gitDiffWithPageDownColor",
        input_file="gitLongDiffColor.txt",
        inputs=[" ", " "],
        with_attributes=True,
    ),
    ScreenTestCase(
        "gitDiffWithValidation",
        input_file="gitDiffSomeExist.txt",
        validate_file_exists=True,
        with_attributes=True,
    ),
    ScreenTestCase(
        "longFileNames",
        input_file="longFileNames.txt",
        validate_file_exists=False,
        with_attributes=False,
        screen_config={
            "maxX": 20,
            "maxY": 30,
        },
    ),
    ScreenTestCase(
        "longFileNamesWithBeforeTextBug",
        input_file="longFileNamesWithBeforeText.txt",
        validate_file_exists=False,
        with_attributes=False,
        inputs=["f"],
        screen_config={
            "maxX": 95,
            "maxY": 40,
        },
    ),
    ScreenTestCase(
        "dontWipeChrome",
        input_file="gitDiffColor.txt",
        with_attributes=True,
        validate_file_exists=False,
        inputs=["DOWN", "f", "f", "f", "UP"],
        screen_config={"maxX": 201, "maxY": 40},
        past_screens=[0, 1, 2, 3, 4],
    ),
    ScreenTestCase(
        "longFileTruncation",
        input_file="superLongFileNames.txt",
        with_attributes=True,
        inputs=["DOWN", "f"],
        screen_config={"maxX": 60, "maxY": 20},
    ),
    ScreenTestCase(
        "xModeWithSelect",
        input_file="gitDiff.txt",
        with_attributes=True,
        inputs=["x", "E", "H"],
    ),
    ScreenTestCase(
        "gitAbbreivatedFiles",
        input_file="gitAbbreviatedFiles.txt",
        with_attributes=True,
        inputs=["f", "j"],
    ),
    ScreenTestCase("selectAllBug", input_file="gitLongDiff.txt", inputs=["A"]),
    ScreenTestCase(
        "allInputBranch", input_file="gitBranch.txt", args=["-ai"], inputs=["j", "f"]
    ),
    ScreenTestCase(
        "abbreviatedLineSelect",
        input_file="longLineAbbreviated.txt",
        validate_file_exists=False,
        inputs=["j", "j", "f"],
    ),
    ScreenTestCase(
        "longListPageUpAndDown",
        input_file="longList.txt",
        inputs=["NPAGE", "NPAGE", "NPAGE", "PPAGE"],
        validate_file_exists=False,
    ),
    ScreenTestCase(
        "longListHomeKey",
        input_file="longList.txt",
        inputs=[" ", " ", "HOME"],
        with_attributes=True,
        validate_file_exists=False,
        screen_config={"maxY": 10},
    ),
    ScreenTestCase(
        "longListEndKey",
        input_file="longList.txt",
        inputs=["END"],
        with_attributes=True,
        validate_file_exists=False,
        screen_config={"maxY": 10},
    ),
    ScreenTestCase(
        "tonsOfFiles",
        input_file="tonsOfFiles.txt",
        inputs=["A", "c"],
        validate_file_exists=False,
        past_screen=1,
        screen_config={"maxY": 30},
    ),
    ScreenTestCase(
        "fileNameWithSpacesDescription",
        input_file="fileNamesWithSpaces.txt",
        inputs=["d"],
        validate_file_exists=True,
        screen_config={
            "maxX": 201,
        },
    ),
]


class TestScreenLogic(unittest.TestCase):
    def testScreenInputs(self):
        seen_cases: Dict[str, bool] = {}
        for test_case in SCREEN_TEST_CASES:
            # make sure its not copy pasta-ed
            test_name = test_case.name
            self.assertFalse(
                seen_cases.get(test_name, False), "Already seen %s " % test_name
            )
            seen_cases[test_name] = True

            char_inputs = ["q"]  # we always quit at the end
            char_inputs = test_case.inputs + char_inputs

            args = test_case.args
            screen_data = screen_test_runner.getRowsFromScreenRun(
                inputFile=test_case.input_file,
                charInputs=char_inputs,
                screenConfig=test_case.screen_config,
                printScreen=False,
                pastScreen=test_case.past_screen,
                pastScreens=test_case.past_screens,
                args=args,
                validateFileExists=test_case.validate_file_exists,
                allInput=("-ai" in args or "--all-input" in args),
            )

            self.compareToExpected(test_case, test_name, screen_data)
            print("Tested %s " % test_name)

    def compareToExpected(self, test_case, test_name, screen_data):
        TestScreenLogic.maybeMakeExpectedDir()
        (actual_lines, actual_attributes) = screen_data

        if test_case.with_attributes:
            self.compareLinesAndAttributesToExpected(test_name, screen_data)
        else:
            self.compareLinesToExpected(test_name, actual_lines)

    def compareLinesAndAttributesToExpected(self, test_name, screen_data):
        (actual_lines, actual_attributes) = screen_data
        actual_merged_lines = []
        for actual_line, attributeLine in zip(actual_lines, actual_attributes):
            actual_merged_lines.append(actual_line)
            actual_merged_lines.append(attributeLine)

        self.outputIfNotFile(test_name, "\n".join(actual_merged_lines))
        file = open(TestScreenLogic.getExpectedFile(test_name))
        expected_merged_lines = file.read().split("\n")
        file.close()

        self.assertEqualLines(test_name, actual_merged_lines, expected_merged_lines)

    def compareLinesToExpected(self, test_name, actual_lines):
        self.outputIfNotFile(test_name, "\n".join(actual_lines))

        file = open(TestScreenLogic.getExpectedFile(test_name))
        expected_lines = file.read().split("\n")
        file.close()

        self.assertEqualLines(test_name, actual_lines, expected_lines)

    def outputIfNotFile(self, test_name, output):
        expected_file = TestScreenLogic.getExpectedFile(test_name)
        if os.path.isfile(expected_file):
            return

        print("Could not find file %s so outputting..." % expected_file)
        file = open(expected_file, "w")
        file.write(output)
        file.close()
        self.fail("File outputted, please inspect %s for correctness" % expected_file)

    def assertEqualNumLines(self, test_name, actual_lines, expected_lines):
        self.assertEqual(
            len(actual_lines),
            len(expected_lines),
            "%s test: Actual lines was %d but expected lines was %d"
            % (test_name, len(actual_lines), len(expected_lines)),
        )

    def assertEqualLines(self, test_name, actual_lines, expected_lines):
        self.assertEqualNumLines(test_name, actual_lines, expected_lines)
        expected_file = TestScreenLogic.getExpectedFile(test_name)
        glob_needle = " (glob)"
        for index, expected_line in enumerate(expected_lines):
            actual_line = actual_lines[index]
            error_message = (
                'Line %d did not match for test %s:\n\nExpected:"%s"\nActual  :"%s"'
                % (index + 1, expected_file, expected_line, actual_line)
            )
            if expected_line.endswith(glob_needle):
                self.assertEqualWithGlob(
                    expected_line[: -len(glob_needle)], actual_line, error_message
                )
            else:
                self.assertEqual(expected_line, actual_line, error_message)

    def assertEqualWithGlob(self, expected_line, actual_line, error_message):
        # Escape all regex symbols and replace "*" with ".*"
        pattern = ".*".join(map(re.escape, expected_line.split("*")))
        self.assertTrue(re.match(pattern, actual_line), error_message)

    @staticmethod
    def getExpectedFile(test_name):
        return os.path.join(EXPECTED_DIR, test_name + ".txt")

    @staticmethod
    def maybeMakeExpectedDir():
        if not os.path.isdir(EXPECTED_DIR):
            os.makedirs(EXPECTED_DIR)


if __name__ == "__main__":
    unittest.main()
