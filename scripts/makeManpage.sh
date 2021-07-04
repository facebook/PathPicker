#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
command -v a2x >/dev/null 2>&1 || { echo >&2 "I require a2x provided by asciidoc, but it's not installed.  Aborting."; exit 1; }
(cd src && python3 -m pathpicker.usage_strings > manpage.adoc)
a2x --format manpage "src/manpage.adoc" --destination-dir debian/usr/share/man/man1/
