#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
PTH="$(pwd)"
VERSION="$(python "$PTH/../src/version.py")"
DATETIME=$(date '+%a, %d %b %Y %H:%M:%S %z')

echo "Building fpp version $VERSION at $DATETIME"
mkdir -p "$PTH/usr/bin" &&
  mkdir -p "$PTH/usr/share/pathpicker/src/"

sed s#__version__#"$VERSION"# < "$PTH/DEBIAN/control" > "$PTH/DEBIAN/control.modif"
mv "$PTH/DEBIAN/control.modif" "$PTH/DEBIAN/control"

echo "===================="
echo "Control file is:"
echo "===================="
cat "$PTH/DEBIAN/control"
echo "===================="

cp -R "$PTH/../src" "$PTH/usr/share/pathpicker" &&
  cp "$PTH/../fpp" "$PTH/usr/share/pathpicker/fpp" &&
  cd "$PTH/usr/bin/"

echo "Creating symlink..."
ln -f -s ../share/pathpicker/fpp fpp
sed s#__version__#"$VERSION"# < "$PTH/usr/share/doc/pathpicker/changelog" > "$PTH/usr/share/doc/pathpicker/changelog.modif"
sed s#__date_timestamp__#"$DATETIME"# < "$PTH/usr/share/doc/pathpicker/changelog.modif" > "$PTH/usr/share/doc/pathpicker/changelog"

echo "===================="
echo "Changelog is:"
echo "===================="
cat  "$PTH/usr/share/doc/pathpicker/changelog"
echo "===================="

echo "Gziping..."
gzip -9 "$PTH/usr/share/doc/pathpicker/changelog" &&
  rm "$PTH/usr/share/doc/pathpicker/changelog.modif"

echo "Setting permissions..."
cd "$PTH"
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;

echo "Building package..."
rm "$PTH/package.sh"
chmod 755 usr/share/pathpicker/fpp
fakeroot -- sh -c "chown -R root:root * && dpkg --build ./ ../fpp_${VERSION}_noarch.deb ;"
echo "Restoring template files..."
cd -
git checkout HEAD -- "$PTH/DEBIAN/control" "$PTH/usr/share/doc/pathpicker/changelog" "$PTH/package.sh"
chmod 777 "$PTH/package.sh"

echo 'Done! Check out fpp.deb'
