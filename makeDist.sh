#!/bin/bash
VERSION="0.5.3"
DEST="./dist/fpp.$VERSION.tar.gz"
tar -cf $DEST src/*.py fpp
git add $DEST

sed -i '' -e "s#url .*#url \"https://facebook.github.io/PathPicker/dist/fpp.$VERSION.tar.gz\"#g" ./fpp.rb
HASH=$(cat $DEST | shasum -a 256 | cut -d " " -f 1)
sed -i '' -e "s#sha256 .*#sha256 \"$HASH\"#g" ./fpp.rb

NUMFILES=$(git status -sb | wc -l)
if (( NUMFILES > 4 )); then
  echo "Git may include other changes aborting"
  exit 1
fi

echo "Pushing distribution update"
git checkout master && git commit -am "Distribution update" && git push
git checkout gh-pages && git rebase master && git push
git checkout master
