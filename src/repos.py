# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# If you are using a code grep query service and want to resolve
# certain global symbols to local directories,
# add them as REPOS below. We will essentially replace a global
# match against something like:
#   www/myFile.py
# to:
#   ~/www/myFile.py
REPOS = ['www']
