#!/bin/bash
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# get the directory of this script so we can execute the related python
WHEREAMI=$0

# Follow until we get our symlink resolved, since
# homebrew has multiple hops.
while [ -h "$WHEREAMI" ]; do
  WHEREAMI=$(dirname "$WHEREAMI")"/"$(readlink "$WHEREAMI")
done
BASEDIR=$(dirname "$WHEREAMI")
BASEDIR=$(cd $BASEDIR && pwd)

for opt in "$@"; do
  if [ "$opt" == "--debug" ]; then
    echo "Executing from '$BASEDIR'"
  fi
done

# Until we have Python 3.0 support, lets check
# if we have Python2 available directly and (if so)
# use that instead. This helps on linux checkouts
PYTHONCMD="python"
if type python2 &> /dev/null; then
  PYTHONCMD="python2"
fi

# we need to handle the --help option outside the python
# flow since otherwise we will move into input selection...
for opt in "$@"; do
  if [ "$opt" == "--help" -o "$opt" == "-h" ]; then
    $PYTHONCMD "$BASEDIR/src/printHelp.py"
    exit 0
  fi
done

# process input from pipe and store as pickled file
$PYTHONCMD "$BASEDIR/src/processInput.py"
# now choose input and...
exec 0<&-
$PYTHONCMD "$BASEDIR/src/choose.py" < /dev/tty
# execute the output bash script
sh ~/.fbPager.sh < /dev/tty
