#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

if ! type autopep8 > /dev/null; then
  echo "'autopep8' required for build."
  exit 1;
fi

PEPLINES=$(autopep8 --recursive ./src/ --diff | wc -l)
if (( PEPLINES > 0 )); then
  echo "Not Pep8 compliant:";
  autopep8 --recursive ./src/ --diff
  exit 1;
else
  echo "Pep8 Compliant!"
fi

cd ./src/__tests__/
python testParsing.py && python testScreen.py && python testKeyBindingsParsing.py > /dev/null
if [ $? -eq 0 ]
then
  echo "Tests passed!"
else
  echo "Tests failed :*("
  exit 1
fi
