# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

# If you are using a code grep query service and want to resolve
# certain global symbols to local directories,
# add them as REPOS below. We will essentially replace a global
# match against something like:
#   www/myFile.py
# to:
#   ~/www/myFile.py
REPOS = ['www']
