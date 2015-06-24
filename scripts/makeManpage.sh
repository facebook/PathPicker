#!/bin/bash
command -v a2x >/dev/null 2>&1 || { echo >&2 "I require a2x provided by asciidoc, but it's not installed.  Aborting."; exit 1; }
python src/usageStrings.py > manpage.adoc;
a2x --doctype manpage --format manpage manpage.adoc --destination-dir ./debian/usr/share/man/man1/;
gzip -9 ./debian/usr/share/man/man1/fpp.1;
