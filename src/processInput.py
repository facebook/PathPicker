# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
import os
import pickle
import re

import parse
import format
import stateFiles

USAGE_INTRO = '''
Welcome to fpp, the Facebook PathPicker! We hope your stay
with us is enjoyable.

To get started with fpp, pipe some kind of terminal output into the program.
Examples include:

    * git status | fpp
    * git show | fpp
    * git diff HEAD master | fpp
    * git diff HEAD~10 --numstat | fpp
    * grep -r "Banana" . | fpp
    * find . -iname "*.js" | fpp

Once fpp parses your input (and something that looks like a file matches), it
will put you inside a pager that will allow you to select files with the
following commands:
'''

USAGE_PAGE_HEADER = '''
== Navigation ==

'''

USAGE_PAGE = '''
    * [f] toggle the selection of a file
    * [A] toggle selection of all (unique) files
    * [down arrow|j] move downward by 1
    * [up arrow|k] move upward by 1
    * [<space>] page down
    * [b] page up

Once you have your files selected, you can
either open them in your favorite
text editor or execute commands with
them via command mode:

    * [<Enter>] open all selected files
        (or file under cursor if none selected)
        in $EDITOR
    * [c] enter command mode
'''

USAGE_COMMAND_HEADER = '''
== Command Mode ==

'''

USAGE_COMMAND = '''
Command mode is helpful when you want to
execute bash commands with the filenames
you have selected. By default the filenames
are appended automatically to command you
enter before it is executed, so all you have
to do is type the prefix. Some examples:

    * git add
    * git checkout HEAD~1 --
    * rm -rf

These commands get formatted into:
    * git add file1 file2 # etc
    * git checkout HEAD~1 -- file1 file2
    * rm -rf file1 file2 # etc

If your command needs filenames in the middle,
the token "$F" will be replaced with your
selected filenames if it is found in the command
string. Examples include:

    * scp $F dev:~/backup
    * mv $F ../over/here

Which format to:
    * scp file1 file2 dev:~/backup
    * mv file1 file2 ../over/here
'''

USAGE_CONFIGURATION = '''
== Configuration ==


PathPicker offers a bit of configuration currently with more to come
in the future.

~ Editor ~

The $FPP_EDITOR environment variable can be set to tell PathPicker
which editor to open the selected files with. If that variable
is not set, $EDITOR is used the next fallback, with "vim" as a last resort.

~ Keep-Open ~

Use the --keep-open or -ko flag to avoid closing PathPicker once
a file selection or command is performed. This will loop the program
until Ctrl-C is used to terminate the process.

'''

USAGE_TAIL = '''
That's a fairly in-depth overview of Facebook PathPicker.
We also provide help along the way as you
use the app, so don't worry and jump on in!
'''

USAGE_STR = USAGE_INTRO + \
    USAGE_PAGE_HEADER + \
    USAGE_PAGE + \
    USAGE_COMMAND_HEADER + \
    USAGE_COMMAND + \
    USAGE_CONFIGURATION + \
    USAGE_TAIL

decorator = '*' * 80
USAGE_STR = decorator + '\n' + USAGE_STR + '\n' + decorator


def getLineObjs():
    inputLines = sys.stdin.readlines()
    lineObjs = {}
    for index, line in enumerate(inputLines):
        line = line.replace('\t', '    ')
        line = re.sub(r'\x1b[^mK]*(m|K)', '', line)
        result = parse.matchLine(line)

        if not result:
            simple = format.SimpleLine(line, index)
            lineObjs[index] = simple
            continue
        match = format.LineMatch(line, result, index)
        lineObjs[index] = match
    return lineObjs


def doProgram():
    filePath = stateFiles.getPickleFilePath()
    lineObjs = getLineObjs()
    # pickle it so the next program can parse it
    pickle.dump(lineObjs, open(filePath, 'wb'))


def usage():
    print(USAGE_STR)


if __name__ == '__main__':
    if sys.stdin.isatty():
        if os.path.isfile(stateFiles.getPickleFilePath()):
            print('Using old result...')
        else:
            usage()
        # let the next stage parse the old version
        sys.exit(0)
    else:
        # delete the old selection
        print('getting input')
        selectionPath = stateFiles.getSelectionFilePath()
        if os.path.isfile(selectionPath):
            os.remove(selectionPath)

        doProgram()
        sys.exit(0)
