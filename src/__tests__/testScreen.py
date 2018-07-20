# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
sys.path.insert(0, '../')
import unittest
import os

import screenTestRunner

EXPECTED_DIR = './expected/'
screenTestCases = [{
    'name': 'simpleLoadAndQuit',
}, {
    'name': 'tallLoadAndQuit',
    'screenConfig': {
        'maxX': 140,
        'maxY': 60,
    },
}, {
    'name': 'selectFirst',
    'inputs': ['f'],
}, {
    'name': 'selectFirstWithDown',
    'inputs': ['F'],
}, {
    'name': 'selectDownSelect',
    'inputs': ['f', 'j', 'f'],
}, {
    'name': 'selectWithDownSelect',
    'inputs': ['F', 'f'],
}, {
    'name': 'selectDownSelectInverse',
    'inputs': ['f', 'j', 'f', 'A'],
}, {
    'name': 'selectWithDownSelectInverse',
    'inputs': ['F', 'F', 'A'],
}, {
    'name': 'selectTwoCommandMode',
    'input': 'absoluteGitDiff.txt',
    'inputs': ['f', 'j', 'f', 'c'],
    'pastScreen': 3
}, {
    'name': 'selectAllFromArg',
    'input': 'absoluteGitDiff.txt',
    'args': ["-a"],
}, {
    'name': 'executeKeysEndKeySelectLast',
    'args': ["-e", "END", "f"],
}, {
    'name': 'selectCommandWithPassedCommand',
    'input': 'absoluteGitDiff.txt',
    # the last key "a" is so we quit from command mode
    # after seeing the warning
    'withAttributes': True,
    'inputs': ['f', 'c', 'a'],
    'pastScreen': 1,
    'args': ["-c 'git add'"]
}, {
    'name': 'simpleWithAttributes',
    'withAttributes': True
}, {
    'name': 'simpleSelectWithAttributes',
    'withAttributes': True,
    'inputs': ['f', 'j'],
}, {
    'name': 'simpleSelectWithColor',
    'input': 'gitDiffColor.txt',
    'withAttributes': True,
    'inputs': ['f', 'j'],
    'screenConfig': {
        'maxX': 200,
        'maxY': 40,
    },
}, {
    'name': 'gitDiffWithScroll',
    'input': 'gitDiffNoStat.txt',
    'inputs': ['f', 'j'],
}, {
    'name': 'gitDiffWithScrollUp',
    'input': 'gitLongDiff.txt',
    'inputs': ['k', 'k'],
}, {
    'name': 'gitDiffWithPageDown',
    'input': 'gitLongDiff.txt',
    'inputs': [' ', ' '],
}, {
    'name': 'gitDiffWithPageDownColor',
    'input': 'gitLongDiffColor.txt',
    'inputs': [' ', ' '],
    'withAttributes': True,
}, {
    'name': 'gitDiffWithValidation',
    'input': 'gitDiffSomeExist.txt',
    'validateFileExists': True,
    'withAttributes': True,
}, {
    'name': 'longFileNames',
    'input': 'longFileNames.txt',
    'validateFileExists': False,
    'withAttributes': False,
    'screenConfig': {
        'maxX': 20,
        'maxY': 30,
    }
}, {
    'name': 'longFileNamesWithBeforeTextBug',
    'input': 'longFileNamesWithBeforeText.txt',
    'validateFileExists': False,
    'withAttributes': False,
    'inputs': ['f'],
    'screenConfig': {
        'maxX': 95,
        'maxY': 40,
    }
}, {
    'name': 'dontWipeChrome',
    'input': 'gitDiffColor.txt',
    'withAttributes': True,
    'validatesFileExists': False,
    'inputs': ['DOWN', 'f', 'f', 'f', 'UP'],
    'screenConfig': {
        'maxX': 201,
        'maxY': 40
    },
    'pastScreens': [0, 1, 2, 3, 4]
}, {
    'name': 'longFileTruncation',
    'input': 'superLongFileNames.txt',
    'withAttributes': True,
    'inputs': ['DOWN', 'f'],
    'screenConfig': {
        'maxX': 60,
        'maxY': 20
    },
}, {
    'name': 'xModeWithSelect',
    'input': 'gitDiff.txt',
    'withAttributes': True,
    'inputs': ['x', 'E', 'H'],
}, {
    'name': 'gitAbbreivatedFiles',
    'input': 'gitAbbreviatedFiles.txt',
    'withAttributes': True,
    'inputs': ['f', 'j'],
}, {
    'name': 'selectAllBug',
    'input': 'gitLongDiff.txt',
    'inputs': ['A'],
}, {
    'name': 'allInputBranch',
    'input': 'gitBranch.txt',
    'args': ['-ai'],
    'inputs': ['j', 'f'],
}, {
    'name': 'abbreviatedLineSelect',
    'input': 'longLineAbbreviated.txt',
    'validateFileExists': False,
    'inputs': ['j', 'j', 'f'],
}, {
    'name': 'longListPageUpAndDown',
    'input': 'longList.txt',
    'inputs': ['NPAGE', 'NPAGE', 'NPAGE', 'PPAGE'],
    'validateFileExists': False,
}, {
    'name': 'longListHomeKey',
    'input': 'longList.txt',
    'inputs': [' ', ' ', 'HOME'],
    'withAttributes': True,
    'validateFileExists': False,
    'screenConfig': {
        'maxY': 10
    }
}, {
    'name': 'longListEndKey',
    'input': 'longList.txt',
    'inputs': ['END'],
    'withAttributes': True,
    'validateFileExists': False,
    'screenConfig': {
        'maxY': 10
    }
}, {
    'name': 'tonsOfFiles',
    'input': 'tonsOfFiles.txt',
    'inputs': ['A', 'c'],
    'validateFileExists': False,
    'pastScreen': 1,
    'screenConfig': {
        'maxY': 30
    }
}]


class TestScreenLogic(unittest.TestCase):

    def testScreenInputs(self):
        seenCases = {}
        for testCase in screenTestCases:
            # make sure its not copy pasta-ed
            testName = testCase['name']
            self.assertFalse(
                seenCases.get(testName, False), 'Already seen %s ' % testName)
            seenCases[testName] = True

            charInputs = ['q']  # we always quit at the end
            charInputs = testCase.get('inputs', []) + charInputs

            args = testCase.get('args', [])
            screenData = screenTestRunner.getRowsFromScreenRun(
                inputFile=testCase.get('input', 'gitDiff.txt'),
                charInputs=charInputs,
                screenConfig=testCase.get('screenConfig', {}),
                printScreen=False,
                pastScreen=testCase.get('pastScreen', None),
                pastScreens=testCase.get('pastScreens', None),
                args=args,
                validateFileExists=testCase.get('validateFileExists', False),
                allInput=('-ai' in args or '--all-input' in args),
            )

            self.compareToExpected(testCase, testName, screenData)
            print('Tested %s ' % testName)

    def compareToExpected(self, testCase, testName, screenData):
        TestScreenLogic.maybeMakeExpectedDir()
        (actualLines, actualAttributes) = screenData

        if testCase.get('withAttributes', False):
            self.compareLinesAndAttributesToExpected(testName, screenData)
        else:
            self.compareLinesToExpected(testName, actualLines)

    def compareLinesAndAttributesToExpected(self, testName, screenData):
        (actualLines, actualAttributes) = screenData
        actualMergedLines = []
        for actualLine, attributeLine in zip(actualLines, actualAttributes):
            actualMergedLines.append(actualLine)
            actualMergedLines.append(attributeLine)

        self.outputIfNotFile(testName, '\n'.join(actualMergedLines))
        file = open(TestScreenLogic.getExpectedFile(testName))
        expectedMergedLines = file.read().split('\n')
        file.close()

        self.assertEqualLines(testName, actualMergedLines, expectedMergedLines)

    def compareLinesToExpected(self, testName, actualLines):
        self.outputIfNotFile(testName, '\n'.join(actualLines))

        file = open(TestScreenLogic.getExpectedFile(testName))
        expectedLines = file.read().split('\n')
        file.close()

        self.assertEqualLines(testName, actualLines, expectedLines)

    def outputIfNotFile(self, testName, output):
        expectedFile = TestScreenLogic.getExpectedFile(testName)
        if os.path.isfile(expectedFile):
            return

        print('Could not find file %s so outputting...' % expectedFile)
        file = open(expectedFile, 'w')
        file.write(output)
        file.close()
        self.fail(
            'File outputted, please inspect %s for correctness' % expectedFile)

    def assertEqualNumLines(self, testName, actualLines, expectedLines):
        self.assertEqual(
            len(actualLines),
            len(expectedLines),
            '%s test: Actual lines was %d but expected lines was %d' % (
                testName, len(actualLines), len(expectedLines)),
        )

    def assertEqualLines(self, testName, actualLines, expectedLines):
        self.assertEqualNumLines(testName, actualLines, expectedLines)
        expectedFile = TestScreenLogic.getExpectedFile(testName)
        for index, expectedLine in enumerate(expectedLines):
            actualLine = actualLines[index]
            self.assertEqual(
                expectedLine,
                actualLine,
                'Line %d did not match for test %s:\n\nExpected:"%s"\nActual  :"%s"' % (
                    index, expectedFile, expectedLine, actualLine),
            )

    @staticmethod
    def getExpectedFile(testName):
        return os.path.join(EXPECTED_DIR, testName + '.txt')

    @staticmethod
    def maybeMakeExpectedDir():
        if not os.path.isdir(EXPECTED_DIR):
            os.makedirs(EXPECTED_DIR)


if __name__ == '__main__':
    unittest.main()
