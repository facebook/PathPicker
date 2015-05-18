PTH="$(pwd)"
VERSION="$(python $PTH/../src/version.py)"
DATETIME=$(date '+%a, %d %b %Y %H:%M:%S %z')
mkdir $PTH/usr/bin
mkdir -p $PTH/usr/share/pathpicker/src/
sed s#__version__#"$VERSION"# < $PTH/DEBIAN/control > $PTH/DEBIAN/control.modif
mv $PTH/DEBIAN/control.modif $PTH/DEBIAN/control
cp -R $PTH/../src $PTH/usr/share/pathpicker
cp $PTH/../fpp $PTH/usr/share/pathpicker/fpp
cd $PTH/usr/bin/
ln --symbolic ../share/pathpicker/fpp fpp
sed s#__version__#"$VERSION"# < $PTH/usr/share/doc/pathpicker/changelog > $PTH/usr/share/doc/pathpicker/changelog.modif
sed s#__date_timestamp__#"$DATETIME"# < $PTH/usr/share/doc/pathpicker/changelog.modif > $PTH/usr/share/doc/pathpicker/changelog
gzip -9 $PTH/usr/share/doc/pathpicker/changelog
rm $PTH/usr/share/doc/pathpicker/changelog.modif
cd $PTH
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
chmod 755 usr/share/pathpicker/fpp
fakeroot -- sh -c ' chown -R root:root * && dpkg --build ./ ../fpp.deb ;'

