#!/bin/bash
VERSION="0.5.0"
DEST="./dist/fpp.$VERSION.tar.gz"
tar -cf $DEST src/*.py fpp
git add $DEST
