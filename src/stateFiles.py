# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import os

FPP_DIR = '~/.fpp'
PICKLE_FILE = '.pickle'
SELECTION_PICKLE = '.selection.pickle'
OUTPUT_FILE = '.fpp.sh'

def assertDirCreated():
    path = os.path.expanduser(FPP_DIR)
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def getPickleFilePath():
    assertDirCreated()
    return os.path.expanduser(os.path.join(FPP_DIR, PICKLE_FILE))

def getSelectionFilePath():
    assertDirCreated()
    return os.path.expanduser(os.path.join(FPP_DIR, SELECTION_PICKLE))

def getScriptOutputFilePath():
    assertDirCreated()
    return os.path.expanduser(os.path.join(FPP_DIR, OUTPUT_FILE))
