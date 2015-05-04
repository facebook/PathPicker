#!/bin/bash
VERSION="0.5.3"
DEST="./dist/fpp.$VERSION.tar.gz"
tar -cf $DEST src/*.py fpp
git add $DEST

sed -i '' -e "s#url .*#url \"https://facebook.github.io/PathPicker/dist/fpp.$VERSION.tar.gz\"#g" ./fpp.rb
HASH=$(cat $DEST | shasum -a 256 | cut -d " " -f 1)
sed -i '' -e "s#sha256 .*#sha256 \"$HASH\"#g" ./fpp.rb

echo "Recipe updated with hash from $DEST"
