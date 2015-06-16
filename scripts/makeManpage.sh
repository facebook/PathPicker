#!/bin/bash
python src/usageStrings.py > manpage.adoc;
a2x --doctype manpage --format manpage manpage.adoc --destination-dir ./debian/usr/share/man/man1/;

