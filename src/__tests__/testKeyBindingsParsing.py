# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import sys

sys.path.insert(0, '../')

from keyBindingsForTest import KEY_BINDINGS_FOR_TEST_CONFIG_CONTENT
from keyBindingsForTest import KeyBindingsForTest
from keyBindings import KeyBindings
import tempfile
import keyBindings
import unittest


class TestKeyBindingsParser(unittest.TestCase):

    def testIgnoreNonExistingConfigurationFile(self):
        file = tempfile.NamedTemporaryFile(delete=True)
        file.close()

        parser = KeyBindings(file.name)

        self.assertEqual(
            parser.bindings,
            [],
            'The parser did not return an empty list, when initialized with a non-existent file: %s' % (
                parser.bindings)
        )

    def testStandardParsing(self):
        file = tempfile.NamedTemporaryFile(mode='wt', delete=False)
        file.write(KEY_BINDINGS_FOR_TEST_CONFIG_CONTENT)
        file.close()

        parser = KeyBindings(file.name)

        actualResult = sorted(parser.bindings)
        expectedResult = KeyBindingsForTest().bindings

        self.assertEqual(
            actualResult,
            expectedResult,
            'The parser did not properly parse the test file\n\nExpected:"%s"\nActual  :"%s"' % (
                expectedResult, actualResult)
        )


if __name__ == '__main__':
    unittest.main()
