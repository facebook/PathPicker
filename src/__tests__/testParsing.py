# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import print_function

import sys
import unittest
import os
sys.path.insert(0, '../')

import parse
from localTestCases import LOCAL_TEST_CASES
from formattedText import FormattedText
import format

fileTestCases = [{
    'input': 'html/js/hotness.js',
    'match': True,
    'file': 'html/js/hotness.js'
}, {
    'input': '/absolute/path/to/something.txt',
    'match': True,
    'file': '/absolute/path/to/something.txt'
}, {
    'input': '/html/js/hotness.js42',
    'match': True,
    'file': '/html/js/hotness.js42'
}, {
    'input': '/html/js/hotness.js',
    'match': True,
    'file': '/html/js/hotness.js'
}, {
    'input': './asd.txt:83',
    'match': True,
    'file': './asd.txt',
    'num': 83
}, {
    'input': '.env.local',
    'match': True,
    'file': '.env.local'
}, {
    'input': '.gitignore',
    'match': True,
    'file': '.gitignore'
}, {
    'input': 'tmp/.gitignore',
    'match': True,
    'file': 'tmp/.gitignore'
}, {
    'input': '.ssh/.gitignore',
    'match': True,
    'file': '.ssh/.gitignore'
}, {
    'input': '.ssh/known_hosts',
    'match': True,
    'file': '.ssh/known_hosts'

    # For now, don't worry about matching the following case perfectly,
    # simply because it's complicated.
    # }, {
    #    'input': '~/.ssh/known_hosts',
    #    'match': True,

}, {
    # Arbitrarily ignore really short dot filenames
    'input': '.a',
    'match': False,
}, {
    'input': 'flib/asd/ent/berkeley/two.py-22',
    'match': True,
    'file': 'flib/asd/ent/berkeley/two.py',
    'num': 22
}, {
    'input': 'flib/foo/bar',
    'match': True,
    'file': 'flib/foo/bar'
}, {
    'input': 'flib/foo/bar ',  # note space
    'match': True,
    'file': 'flib/foo/bar'
}, {
    'input': 'foo/b ',
    'match': True,
    'file': 'foo/b'
}, {
    'input': 'foo/bar/baz/',
    'match': False
}, {
    'input': 'flib/ads/ads.thrift',
    'match': True,
    'file': 'flib/ads/ads.thrift'
}, {
    'input': 'banana hanana Wilde/ads/story.m',
    'match': True,
    'file': 'Wilde/ads/story.m'
}, {
    'input': 'flib/asd/asd.py two/three/four.py',
    'match': True,
    'file': 'flib/asd/asd.py'
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
    'input':
    '(fbcode/search/places/scorer/PageScorer.cpp:27:46):#include "search/places/scorer/linear_scores/MinutiaeVerbScorer.h',
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
    'file': '~/foo/bar/something.py'
}, {
    'input': '~/foo/bar/inHomeDir.py:22',
    'match': True,
    'file': '~/foo/bar/inHomeDir.py',
    'num': 22,
}, {
    'input': 'blarge assets/retina/victory@2x.png',
    'match': True,
    'file': 'assets/retina/victory@2x.png'
}, {
    'input': '~/assets/retina/victory@2x.png',
    'match': True,
    'file': '~/assets/retina/victory@2x.png'
}, {
    'input': 'So.many.periods.txt',
    'match': True,
    'file': 'So.many.periods.txt'
}, {
    'input': 'So.many.periods.txt~',
    'match': True,
    'file': 'So.many.periods.txt~'
}, {
    'input': '#So.many.periods.txt#',
    'match': True,
    'file': '#So.many.periods.txt#'
}, {
    'input': 'SO.MANY.PERIODS.TXT',
    'match': True,
    'file': 'SO.MANY.PERIODS.TXT'
}, {
    'input': 'blarg blah So.MANY.PERIODS.TXT:22',
    'match': True,
    'file': 'So.MANY.PERIODS.TXT',
    'num': 22
}, {
    'input': 'SO.MANY&&PERIODSTXT',
    'match': False
}, {
    'input': 'test src/categories/NSDate+Category.h',
    'match': True,
    'file': 'src/categories/NSDate+Category.h'
}, {
    'input': '~/src/categories/NSDate+Category.h',
    'match': True,
    'file': '~/src/categories/NSDate+Category.h'
}, {
    'input': 'M    ./inputs/evilFile With Space.txt',
    'match': True,
    'file': './inputs/evilFile With Space.txt',
    'validateFileExists': True,
}, {
    'input': './inputs/evilFile With Space.txt:22',
    'match': True,
    'num': 22,
    'file': './inputs/evilFile With Space.txt',
    'validateFileExists': True,
}, {
    'input': './inputs/annoying Spaces Folder/evilFile With Space2.txt',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/annoying Spaces Folder/evilFile With Space2.txt',
}, {
    'input': './inputs/annoying Spaces Folder/evilFile With Space2.txt:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/annoying Spaces Folder/evilFile With Space2.txt',
}, {
    # with leading space
    'input': ' ./inputs/annoying Spaces Folder/evilFile With Space2.txt:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/annoying Spaces Folder/evilFile With Space2.txt',
}, {
    # git style
    'input': 'M     ./inputs/annoying Spaces Folder/evilFile With Space2.txt:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/annoying Spaces Folder/evilFile With Space2.txt',
}, {
    # files with + in them, silly objective c
    'input': 'M     ./objectivec/NSArray+Utils.h',
    'match': True,
    'file': './objectivec/NSArray+Utils.h',
}, {
    'input': 'NSArray+Utils.h',
    'match': True,
    'file': 'NSArray+Utils.h',
}, {
    # And with filesystem validation just in case
    # the + breaks something
    'input': './inputs/NSArray+Utils.h:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/NSArray+Utils.h',
}, {
    # and our hyphen extension file
    'input': './inputs/blogredesign.sublime-workspace:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/blogredesign.sublime-workspace',
}, {
    # and our hyphen extension file with no dir
    'input': 'inputs/blogredesign.sublime-workspace:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': 'inputs/blogredesign.sublime-workspace',
}, {
    # and our hyphen extension file with no dir or number
    'input': 'inputs/blogredesign.sublime-workspace',
    'validateFileExists': True,
    'match': True,
    'file': 'inputs/blogredesign.sublime-workspace',
}, {
    # and a huge combo of stuff
    'input': './inputs/annoying-hyphen-dir/Package Control.system-bundle',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/annoying-hyphen-dir/Package Control.system-bundle',
}, {
    # and a huge combo of stuff with no prepend
    'input': 'inputs/annoying-hyphen-dir/Package Control.system-bundle',
    'validateFileExists': True,
    'match': True,
    'disableFuzzTest': True,
    'file': 'inputs/annoying-hyphen-dir/Package Control.system-bundle',
}, {
    # and a huge combo of stuff with line
    'input': './inputs/annoying-hyphen-dir/Package Control.system-bundle:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/annoying-hyphen-dir/Package Control.system-bundle',
}, {
    'input': './inputs/svo (install the zip, not me).xml',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/svo (install the zip, not me).xml',
}, {
    'input': './inputs/svo (install the zip not me).xml',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/svo (install the zip not me).xml',
}, {
    'input': './inputs/svo install the zip, not me.xml',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/svo install the zip, not me.xml',
}, {
    'input': './inputs/svo install the zip not me.xml',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/svo install the zip not me.xml',
}, {
    'input': './inputs/annoyingTildeExtension.txt~:42',
    'validateFileExists': True,
    'match': True,
    'num': 42,
    'file': './inputs/annoyingTildeExtension.txt~',
}, {
    'input': 'inputs/.DS_KINDA_STORE',
    'validateFileExists': True,
    'match': True,
    'file': 'inputs/.DS_KINDA_STORE',
}, {
    'input': './inputs/.DS_KINDA_STORE',
    'validateFileExists': True,
    'match': True,
    'file': './inputs/.DS_KINDA_STORE',
}, {
    'input': 'evilFile No Prepend.txt',
    'validateFileExists': True,
    'match': True,
    'disableFuzzTest': True,
    'file': 'evilFile No Prepend.txt',
}, {
    'input': 'file-from-yocto_%.bbappend',
    'validateFileExists': True,
    'match': True,
    'file': 'file-from-yocto_%.bbappend',
}, {
    'input': 'otehr thing ./foo/file-from-yocto_3.1%.bbappend',
    'validateFileExists': True,
    'match': True,
    'file': 'file-from-yocto_3.1%.bbappend',
}, {
    'input': './file-from-yocto_3.1%.bbappend',
    'validateFileExists': True,
    'match': True,
    'file': './file-from-yocto_3.1%.bbappend',
}, {
    'input': 'Gemfile',
    'validateFileExists': False,
    'match': True,
    'disableFuzzTest': True,
    'file': 'Gemfile',
}, {
    'input': 'Gemfilenope',
    'validateFileExists': False,
    'match': False,
    'disableFuzzTest': True,
}]

# local test cases get added as well
fileTestCases += LOCAL_TEST_CASES

prependDirTestCases = [
    {
        'in': 'home/absolute/path.py',
        'out': '/home/absolute/path.py'
    }, {
        'in': '~/www/asd.py',
        'out': os.path.expanduser('~/www/asd.py'),
    }, {
        'in': 'www/asd.py',
        'out': os.path.expanduser('~/www/asd.py'),
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

allInputTestCases = [
    {
        'input': '    ',
        'match': None
    }, {
        'input': ' ',
        'match': None
    }, {
        'input': 'a',
        'match': 'a'
    }, {
        'input': '   a',
        'match': 'a'
    }, {
        'input': 'a    ',
        'match': 'a'
    }, {
        'input': '    foo bar',
        'match': 'foo bar'
    }, {
        'input': 'foo bar    ',
        'match': 'foo bar'
    }, {
        'input': '    foo bar    ',
        'match': 'foo bar'
    }, {
        'input': 'foo bar baz',
        'match': 'foo bar baz'
    }, {
        'input': '	modified:   Classes/Media/YPMediaLibraryViewController.m',
        'match': 'modified:   Classes/Media/YPMediaLibraryViewController.m'
    }, {
        'input': 'no changes added to commit (use "git add" and/or "git commit -a")',
        'match': 'no changes added to commit (use "git add" and/or "git commit -a")'
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
            if testCase.get('disableFuzzTest'):
                continue
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
        lineObj = format.LineMatch(FormattedText(fileLine), result, 0)
        self.assertTrue(
            not lineObj.isResolvable(),
            '"%s" should not be resolvable' % fileLine
        )
        print('Tested unresolvable case.')

    def testResolvable(self):
        toCheck = [case for case in fileTestCases if case['match']]
        for testCase in toCheck:
            result = parse.matchLine(testCase['input'])
            lineObj = format.LineMatch(
                FormattedText(testCase['input']), result, 0)
            self.assertTrue(
                lineObj.isResolvable(),
                'Line "%s" was not resolvable' % testCase['input']
            )
        print('Tested %d resolvable cases.' % len(toCheck))

    def testFileMatch(self):
        for testCase in fileTestCases:
            self.checkFileResult(testCase)
        print('Tested %d cases.' % len(fileTestCases))

    def testAllInputMatches(self):
        for testCase in allInputTestCases:
            result = parse.matchLine(testCase['input'], False, True)

            if not result:
                self.assertTrue(testCase['match'] is None,
                                'Expected a match "%s" where one did not occur.' %
                                testCase['match'])
                continue

            (match, _, _) = result
            self.assertEqual(match, testCase['match'], 'Line "%s" did not match.' %
                             testCase['input'])

        print('Tested %d cases for all-input matching.' %
              len(allInputTestCases))

    def checkFileResult(self, testCase):
        result = parse.matchLine(testCase['input'],
                                 validateFileExists=testCase.get('validateFileExists', False))
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

        self.assertEqual(testCase.get('num', 0), num, 'num matches not equal %d %d for %s'
                         % (testCase.get('num', 0), num, testCase.get('input')))


if __name__ == '__main__':
    unittest.main()
