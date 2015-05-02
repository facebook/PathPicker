#!/bin/bash
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# get the directory of this script so we can execute the related python
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# we need to handle the --help option outside the python
# flow since otherwise we will move into input selection...
for opt in "$@"; do
  if [ "$opt" == "--help" -o "$opt" == "-h" ]; then
    python $DIR/src/printHelp.py
    exit 0
  fi
done

# process input from pipe and store as pickled file
python "$DIR/src/processInput.py"
# now choose input and...
exec 0<&-
python "$DIR/src/choose.py" < /dev/tty
# execute the output bash script
sh ~/.fbPager.sh < /dev/tty

