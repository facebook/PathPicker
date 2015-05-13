# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import curses
import sys
sys.path.insert(0,'../')

import choose
from screenForTest import ScreenForTest
from cursesForTest import CursesForTest

def initScreenTest():
    print('Getting the line objs')
    choose.doProgram(ScreenForTest(), CursesForTest())

if __name__ == '__main__':
    initScreenTest()
