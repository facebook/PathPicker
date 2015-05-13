# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import argparse

class ScreenFlags(object):

    """A class that just represents what flags we pass into
    the screencontrol method -- for instance, if we are in
    record mode. Possibly will be expanded in the future."""

    def __init__(self, isRecordMode=False):
        self.isRecordMode = isRecordMode

    def getIsRecordMode(self):
        return self.isRecordMode

    @staticmethod
    def initFromArgs():
        parser = argparse.ArgumentParser()
        parser.add_argument('-r',
            '--record',
            help='record input and output',
            default=False,
            action='store_true')
        args = parser.parse_args()

        return ScreenFlags(args.record)
