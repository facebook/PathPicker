#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

if ! command -v black &> /dev/null; then
  echo "'black' is required for build."
  exit 1;
fi

if ! black --check ./src/; then
  echo "Not properly formatted!";
  exit 1;
else
  echo "Formatting is good!"
fi

cd ./src/__tests__/
for testname in test*.py; do
    echo "Running: $testname"
    if ! python3 "$testname"; then
        echo "Tests failed :("
        exit 1
    fi
done
