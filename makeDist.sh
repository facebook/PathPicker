#!/bin/bash
VERSION="0.5.1"
DEST="./dist/fpp.$VERSION.tar.gz"
tar -cf $DEST src/*.py fpp
git add $DEST

sed -i -e "s#url .*#url \"https://facebook.github.io/PathPicker/dist/fpp.$VERSION.tar.gz\"#g" ./fpp.rb
