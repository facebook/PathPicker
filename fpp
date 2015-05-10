#!/bin/bash
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

# get the directory of this script so we can execute the related python
# http://stackoverflow.com/a/246128/212110
SOURCE=$0
# resolve $SOURCE until the file is no longer a symlink
while [ -h "$SOURCE" ]; do
  BASEDIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  # if $SOURCE was a relative symlink, we need to resolve it relative to
  # the path where the symlink file was located
  [[ $SOURCE != /* ]] && SOURCE="$BASEDIR/$SOURCE"
done
BASEDIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

PYTHONCMD="python"
# we need to handle the --help option outside the python
# flow since otherwise we will move into input selection...
# Hack to be able to access argument following '-r'/'--regex'
i=0
for opt in "$@"; do
  if [ "$opt" == "--debug" ]; then
    echo "Executing from '$BASEDIR'"
  elif [ "$opt" == "--python3" ]; then
    PYTHONCMD="python3"
  elif [ "$opt" == "--help" -o "$opt" == "-h" ]; then
    $PYTHONCMD "$BASEDIR/src/printHelp.py"
    exit 0
  elif [ "$opt" == "-r" -o "$opt" == "--regex" ]; then
    # Ditto wrt hack
    array=( "$@" )
    CUSTOMREGEX=${array[((i+1))]}
  fi
  i=$((i+1))
done

# process input from pipe and store as pickled file
$PYTHONCMD "$BASEDIR/src/processInput.py" $CUSTOMREGEX
# now choose input and...
exec 0<&-
$PYTHONCMD "$BASEDIR/src/choose.py" < /dev/tty
# execute the output bash script
sh ~/.fpp/.fpp.sh < /dev/tty
