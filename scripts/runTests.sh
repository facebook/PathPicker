#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# get the directory of this script so we can execute the related python
# http://stackoverflow.com/a/246128/212110
SOURCE=$0
# resolve $SOURCE until the file is no longer a symlink
while [ -h "$SOURCE" ]; do
  BASEDIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  # if $SOURCE was a relative symlink, we need to resolve it relative to
  # the path where the symlink file was located
  [[ $SOURCE != /* ]] && SOURCE="$BASEDIR/$SOURCE"
done
BASEDIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
REPO_ROOT="$BASEDIR/.."

if ! command -v black &> /dev/null; then
  echo "'black' is required for build."
  exit 1
fi

if ! isort --check-only --verbose "$REPO_ROOT/src/"; then
  echo "Imports are not sorted properly!"
  exit 1
fi

if ! black --check --verbose "$REPO_ROOT/src/"; then
  echo "Not properly formatted!"
  exit 1
else
  echo "Formatting looks good!"
fi

if ! mypy "$REPO_ROOT/src/"; then
  echo "Typing errors!"
  exit 1
fi

export PYTHONPATH="$REPO_ROOT/src"

cd "$REPO_ROOT/src/tests/"
for testname in test*.py; do
    echo "Running: $testname"
    if ! python3 "$testname"; then
        echo "Tests failed :("
        exit 1
    fi
done
