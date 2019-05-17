#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
VERSION="$(python ./src/version.py)"
DEST="./dist/fpp.$VERSION.tar.gz"
mkdir -p ./dist/
tar -czf $DEST src/*.py fpp

sed -i '' -e "s#url .*#url \"https://github.com/facebook/PathPicker/releases/download/$VERSION/fpp.$VERSION.tar.gz\"#g" ./fpp.rb
HASH=$(cat $DEST | shasum -a 256 | cut -d " " -f 1)
sed -i '' -e "s#^  sha256 .*#  sha256 \"$HASH\"#g" ./fpp.rb

echo "Recipe updated with hash from $DEST"
