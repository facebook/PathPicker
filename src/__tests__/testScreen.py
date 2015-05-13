# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
sys.path.insert(0,'../')
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
    'name': 'selectDownSelect',
    'inputs': ['f', 'j', 'f'],
}, {
    'name': 'selectDownSelectInverse',
    'inputs': ['f', 'j', 'f', 'A'],
}]

class TestScreenLogic(unittest.TestCase):

    def testScreenInputs(self):
        seenCases = {}
        for testCase in screenTestCases:
            # make sure its not copy pasta-ed
            testName = testCase['name']
            self.assertFalse(seenCases.get(testName, False), 'Already seen %s ' % testName)
            seenCases[testName] = True

            charInputs = ['q']  # we always quit at the end
            charInputs = testCase.get('inputs', []) + charInputs
            actualLines = screenTestRunner.getRowsFromScreenRun(
                inputFile=testCase.get('input', 'gitDiff.txt'),
                charInputs=charInputs,
                screenConfig=testCase.get('screenConfig', {}),
                printScreen=False,
            )
            self.compareToExpected(testName, actualLines)
            print('Tested %s ' % testName)

    def compareToExpected(self, testName, actualLines):
        expectedFile = os.path.join(EXPECTED_DIR, testName + '.txt')
        if not os.path.isdir(EXPECTED_DIR):
            os.makedirs(EXPECTED_DIR)
        if not os.path.isfile(expectedFile):
            print('Could not find file %s so outputting...' % expectedFile)
            file = open(expectedFile, 'w')
            file.write('\n'.join(actualLines))
            file.close()
            self.fail('File outputted, please inspect %s for correctness' % expectedFile)
            return

        file = open(expectedFile)
        expectedLines = file.read().split('\n')
        file.close()
        self.assertEqual(
            len(actualLines),
            len(expectedLines),
            'Actual lines was %d but expected lines aws %d' % (len(actualLines), len(expectedLines)),
        )
        for index, expectedLine in enumerate(expectedLines):
            actualLine = actualLines[index]
            self.assertEqual(
                expectedLine,
                actualLine,
                'Lines did not match:\n\nExpected:%s\nActual:%s' % (expectedLine, actualLine),
            )

if __name__ == '__main__':
    unittest.main()
