#!/bin/bash
python src/usageStrings.py > manpage.adoc;
a2x --doctype manpage --format manpage manpage.adoc;

