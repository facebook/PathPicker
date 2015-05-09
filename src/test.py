# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint
from __future__ import print_function

import curses
import os
import unittest

import format
import parse
from utils import ignore_curse_errors


fileTestCases = [{
    'input': 'html/js/hotness.js',
    'match': True,
    'file': 'html/js/hotness.js',
    'num': 0
}, {
    'input': '/absolute/path/to/something.txt',
    'match': True,
    'file': '/absolute/path/to/something.txt',
    'num': 0
}, {
    'input': '/html/js/hotness.js42',
    'match': True,
    'file': '/html/js/hotness.js42',
    'num': 0
}, {
    'input': '/html/js/hotness.js',
    'match': True,
    'file': '/html/js/hotness.js',
    'num': 0
}, {
    'input': './asd.txt:83',
    'match': True,
    'file': './asd.txt',
    'num': 83
}, {
    'input': 'flib/asd/ent/berkeley/two.py-22',
    'match': True,
    'file': 'flib/asd/ent/berkeley/two.py',
    'num': 22
}, {
    'input': 'flib/foo/bar',
    'match': True,
    'file': 'flib/foo/bar',
    'num': 0
}, {
    'input': 'flib/foo/bar ',  # note space
    'match': True,
    'file': 'flib/foo/bar',
    'num': 0
}, {
    'input': 'foo/b ',
    'match': True,
    'file': 'foo/b',
    'num': 0
}, {
    'input': 'foo/bar/baz/',
    'match': False
}, {
    'input': 'flib/ads/ads.thrift',
    'match': True,
    'file': 'flib/ads/ads.thrift',
    'num': 0
}, {
    'input': 'banana hanana Wilde/ads/story.m',
    'match': True,
    'file': 'Wilde/ads/story.m',
    'num': 0
}, {
    'input': 'flib/asd/asd.py two/three/four.py',
    'match': True,
    'file': 'flib/asd/asd.py',
    'num': 0
}, {
    'input': 'asd/asd/asd/ 23',
    'match': False
}, {
    'input': 'foo/bar/TARGETS:23',
    'match': True,
    'num': 23,
    'file': 'foo/bar/TARGETS'
}, {
    'input': 'foo/bar/TARGETS-24',
    'match': True,
    'num': 24,
    'file': 'foo/bar/TARGETS'
}, {
    'input':
    'fbcode/search/places/scorer/PageScorer.cpp:27:46:#include "search/places/scorer/linear_scores/MinutiaeVerbScorer.h',
    'match': True,
    'num': 27,
    'file': 'fbcode/search/places/scorer/PageScorer.cpp'
}, {
    # Pretty intense case
    'input':
    'fbcode/search/places/scorer/TARGETS:590:28:    srcs = ["linear_scores/MinutiaeVerbScorer.cpp"]',
    'match': True,
    'num': 590,
    'file': 'fbcode/search/places/scorer/TARGETS'
}, {
    'input':
    'fbcode/search/places/scorer/TARGETS:1083:27:      "linear_scores/test/MinutiaeVerbScorerTest.cpp"',
    'match': True,
    'num': 1083,
    'file': 'fbcode/search/places/scorer/TARGETS'
}, {
    'input': '~/foo/bar/something.py',
    'match': True,
    'num': 0,
    'file': '~/foo/bar/something.py'
}, {
    'input': '~/foo/bar/inHomeDir.py:22',
    'match': True,
    'num': 22,
    'file': '~/foo/bar/inHomeDir.py'
}, {
    'input': 'blarge assets/retina/victory@2x.png',
    'match': True,
    'num': 0,
    'file': 'assets/retina/victory@2x.png'
}, {
    'input': '~/assets/retina/victory@2x.png',
    'match': True,
    'num': 0,
    'file': '~/assets/retina/victory@2x.png'
}, {
    'input': 'So.many.periods.txt',
    'match': True,
    'num': 0,
    'file': 'So.many.periods.txt'
}, {
    'input': 'SO.MANY.PERIODS.TXT',
    'match': True,
    'num': 0,
    'file': 'SO.MANY.PERIODS.TXT'
}, {
    'input': 'blarg blah So.MANY.PERIODS.TXT:22',
    'match': True,
    'num': 0,  # we ignore the number here
    'file': 'So.MANY.PERIODS.TXT'
}, {
    'input': 'SO.MANY&&PERIODSTXT',
    'match': False
}, {
    'input': 'test src/categories/NSDate+Category.h',
    'match': True,
    'num': 0,
    'file': 'src/categories/NSDate+Category.h'
}, {
    'input': '~/src/categories/NSDate+Category.h',
    'match': True,
    'num': 0,
    'file': '~/src/categories/NSDate+Category.h'
}]

prependDirTestCases = [
    {
        'in': 'home/absolute/path.py',
        'out': '/home/absolute/path.py'
    }, {
        'in': '~/www/asd.py',
        'out': '~/www/asd.py'
    }, {
        'in': 'www/asd.py',
        'out': '~/www/asd.py'
    }, {
        'in': 'foo/bar/baz/asd.py',
        'out': parse.PREPEND_PATH + 'foo/bar/baz/asd.py'
    }, {
        'in': 'a/foo/bar/baz/asd.py',
        'out': parse.PREPEND_PATH + 'foo/bar/baz/asd.py'
    }, {
        'in': 'b/foo/bar/baz/asd.py',
        'out': parse.PREPEND_PATH + 'foo/bar/baz/asd.py'
    }, {
        'in': '',
        'out': ''
    }]


class TestParseFunction(unittest.TestCase):

    def testPrependDir(self):
        for testCase in prependDirTestCases:
            inFile = testCase['in']

            result = parse.prependDir(inFile)
            expected = testCase['out']
            if inFile[0:2] == '~/':
                expected = os.path.expanduser(expected)

            self.assertEqual(expected, result)
        print('Tested %d dir cases.' % len(prependDirTestCases))

    def testFileFuzz(self):
        befores = ['M ', 'Modified: ', 'Changed: ', '+++ ',
                   'Banana asdasdoj pjo ']
        afters = [' * Adapts AdsErrorCodestore to something',
                  ':0:7: var AdsErrorCodeStore', ' jkk asdad']

        for testCase in fileTestCases:
            for before in befores:
                for after in afters:
                    testInput = '%s%s%s' % (before, testCase['input'], after)
                    thisCase = testCase.copy()
                    thisCase['input'] = testInput
                    self.checkFileResult(thisCase)
        print('Tested %d cases for file fuzz.' % len(fileTestCases))

    def testUnresolvable(self):
        fileLine = ".../something/foo.py"
        result = parse.matchLine(fileLine)
        lineObj = format.LineMatch(fileLine, result, 0)
        self.assertTrue(
            not lineObj.is_resolvable,
            '"%s" should not be resolvable' % fileLine
        )
        print('Tested unresolvable case.')

    def testResolvable(self):
        toCheck = [case for case in fileTestCases if case['match']]
        for testCase in toCheck:
            result = parse.matchLine(testCase['input'])
            lineObj = format.LineMatch(testCase['input'], result, 0)
            self.assertTrue(
                lineObj.is_resolvable,
                'Line "%s" was not resolvable' % testCase['input']
            )
        print('Tested %d resolvable cases.' % len(toCheck))

    def testFileMatch(self):
        for testCase in fileTestCases:
            self.checkFileResult(testCase)
        print('Tested %d cases.' % len(fileTestCases))

    def checkFileResult(self, testCase):
        result = parse.matchLine(testCase['input'])
        if not result:
            self.assertFalse(testCase['match'],
                             'Line "%s" did not match any regex' %
                             testCase['input'])
            return

        file, num, match = result
        self.assertTrue(testCase['match'], 'Line "%s" did match' %
                        testCase['input'])

        self.assertEqual(testCase['file'], file, 'files not equal |%s| |%s|' %
                         (testCase['file'], file))

        self.assertEqual(testCase['num'], num, 'num matches not equal %d %d for %s'
                         % (testCase['num'], num, testCase.get('input')))

    def test_ignore_curse_errors_no_exception(self):
        """
        Check that if no exception is raised, the result is still the same.
        """
        with ignore_curse_errors():
            result = 42
        self.assertEqual(result, 42)

    def test_ignore_curse_errors_raise_from_curse(self):
        """
        Check that if an exception from curse is raised, it is ignored.
        """
        # If the exception is ignored, the test passes. Otherwise it doesn't
        # because an exception is raised.
        with ignore_curse_errors():
            raise curses.error

    def test_ignore_curse_errors_raise_exception(self):
        """
        Check that if an exception that is not from curse, it is not ignored.
        """
        with self.assertRaises(LookupError):
            with ignore_curse_errors():
                raise LookupError


if __name__ == '__main__':
    unittest.main()
