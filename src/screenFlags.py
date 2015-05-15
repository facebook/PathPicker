# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function
import argparse

import logger


class ScreenFlags(object):

    """A class that just represents the total set of flags
    available to FPP. Note that some of these are actually
    processsed by the fpp batch file, and not by python.
    However, they are documented here because argsparse is
    clean and easy to use for that purpose.

    The flags that are actually processed and are meaningful
    are

    * c (command)
    * r (record)

    """

    def __init__(self, args):
        self.args = args

    def getIsRecordMode(self):
        return self.args.record

    def getPresetCommand(self):
        return ' '.join(self.args.command)

    @staticmethod
    def getArgParser():
        parser = argparse.ArgumentParser(prog='fpp')
        parser.add_argument('-r',
                            '--record',
                            help='''record input and output. This is
largely used for testing, but you may find it useful for scripting.''',
                            default=False,
                            action='store_true')
        parser.add_argument('-ko',
                            '--keep-open',
                            default=False,
                            action='store_true',
                            help='''keep PathPicker open once
a file selection or command is performed. This will loop the program
until Ctrl-C is used to terminate the process.''')
        parser.add_argument('-c',
                            '--command',
                            help='''You may specify a command while
invoking fpp that will be run once files have been selected. Normally,
fpp opens your editor (see discussion of $EDITOR, $VISUAL, and
$FPP_EDITOR) when you press enter. If you specify a command here,
it will be invoked instead.''',
                            default='',
                            action='store',
                            nargs='+')
        return parser

    @staticmethod
    def initFromArgs(argv):
        (args, chars) = ScreenFlags.getArgParser().parse_known_args(argv)
        return ScreenFlags(args)
