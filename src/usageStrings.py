# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function
from screenFlags import ScreenFlags

MANPAGE_HEADER = '''= fpp(1)
'''

MANPAGE_NAME_SECTION = '''
== NAME

fpp - Facebook PathPicker; a command line tool for selecting files out of bash output
'''

USAGE_INTRO_PRE = '''
Welcome to fpp, the Facebook PathPicker! We hope your stay
with us is enjoyable.
'''

MANPAGE_INTRO_PRE = '''
== INTRO
'''

INTRO = '''
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

USAGE_INTRO = USAGE_INTRO_PRE + INTRO

MANPAGE_SYNOPSIS = '''
== SYNOPSIS

'''

USAGE_PAGE_HEADER = '''
== Navigation ==

'''

USAGE_PAGE = '''
    * [f] toggle the selection of a file
    * [F] toggle and move downward by 1
    * [A] toggle selection of all (unique) files
    * [down arrow|j] move downward by 1
    * [up arrow|k] move upward by 1
    * [<space>] page down
    * [b] page up
    * [x] quick select mode
    * [d] describe file


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
is not set, $VISUAL and then $EDITOR are used as fallbacks,
with "vim" as a last resort.

The $FPP_DISABLE_SPLIT environment variable will disable splitting
files into panes for vim clients (aka sequential editing).

~ Directory ~

PathPicker saves state files for use when starting up, including the
previous input used and selection pickle. By default, these files are saved
in ~/.fpp, but the $FPP_DIR environment variable can be used to tell
PathPicker to use another directory.

~ Colors ~

FPP will understand colors if the piped input uses them. In general, most
tools do not unless requested to do so.

For git, try `git config --global color.ui always` or use the command
line option --color.

For built in commands like `ls`, try `-G` (on Mac, additionally export
CLICOLOR_FORCE in your environment to anything.)

'''

USAGE_COMMAND_LINE = '''
== Command line arguments ==


PathPicker supports some command line arguments, as well.

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
    USAGE_COMMAND_LINE + \
    ScreenFlags.getArgParser().format_help() + \
    USAGE_TAIL

decorator = '*' * 80
USAGE_STR = decorator + '\n' + USAGE_STR + '\n' + decorator


MANPAGE_STR = '\n\n'.join([
    MANPAGE_HEADER,
    MANPAGE_NAME_SECTION,
    MANPAGE_SYNOPSIS,
    # FIXME: asciidoc example block?
    # http://www.methods.co.nz/asciidoc/userguide.html#X48
    ScreenFlags.getArgParser().format_help(),
    MANPAGE_INTRO_PRE,
    INTRO,
    USAGE_PAGE_HEADER,
    USAGE_PAGE,
    USAGE_COMMAND_HEADER,
    USAGE_COMMAND,
    USAGE_CONFIGURATION,
])

if __name__ == '__main__':
    print(MANPAGE_STR)
