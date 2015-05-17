#!/bin/bash
VERSION="$(python ./src/version.py)"
DEST="./dist/fpp.$VERSION.tar.gz"
mkdir -p ./dist/
tar -cf $DEST src/*.py fpp

sed -i '' -e "s#url .*#url \"https://github.com/facebook/PathPicker/releases/download/$VERSION/fpp.$VERSION.tar.gz\"#g" ./fpp.rb
HASH=$(cat $DEST | shasum -a 256 | cut -d " " -f 1)
sed -i '' -e "s#^  sha256 .*#  sha256 \"$HASH\"#g" ./fpp.rb

echo "Recipe updated with hash from $DEST"


# Packaging for debian systems.
# Creates a .deb file in parent directory of the source tree.

DATETIME=$(date '+%a, %d %b %Y %H:%M:%S %z')
sed -i.bak s#__version__#"$VERSION"# ./debian/changelog
sed -i.bak s#__date_timestamp__#"$DATETIME"# ./debian/changelog
debuild -us -uc -i -I
