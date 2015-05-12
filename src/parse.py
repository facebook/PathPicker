# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
import re
import os
import subprocess

import logger

# If you are using a code grep query service and want to resolve
# certain global symbols to local directories,
# add them as REPOS below. We will essentially replace a global
# match against something like:
#   www/myFile.py
# to:
#   ~/www/myFile.py
REPOS = ['www']

MASTER_REGEX = re.compile(
    '(\/?([a-z.A-Z0-9\-_]+\/)+[@a-zA-Z0-9\-_+.]+\.[a-zA-Z0-9]{1,10})[:-]{0,1}(\d+)?')
HOMEDIR_REGEX = re.compile(
    '(~\/([a-z.A-Z0-9\-_]+\/)+[@a-zA-Z0-9\-_+.]+\.[a-zA-Z0-9]{1,10})[:-]{0,1}(\d+)?')
OTHER_BGS_RESULT_REGEX = re.compile(
    '(\/?([a-z.A-Z0-9\-_]+\/)+[a-zA-Z0-9_.]{3,})[:-]{0,1}(\d+)')
JUST_FILE = re.compile(
    r'([.\-_\w]+\.[^\W\d]{1,10})(\s|$|:)+', re.UNICODE)

FILE_NO_PERIODS = re.compile(''.join((
    '(',
    # Recognized files starting with a dot followed by at least 3 characters
    '((\/?([a-z.A-Z0-9\-_]+\/))?\.[a-zA-Z0-9\-_]{3,}[a-zA-Z0-9\-_\/]*)',
    # or
    '|',
    # Recognize files containing at least one slash
    '([a-z.A-Z0-9\-_\/]{1,}\/[a-zA-Z0-9\-_]{1,})',
    ')',
    # Regardless of the above case, here's how the file name should terminate
    '(\s|$|:)+'
)))


# Attempts to resolve the root directory of the
# repository in which path resides (i.e. the current directory).
# both git and hg have commands for this, so let's just use those.
def getRepoPath():
    proc = subprocess.Popen(["git rev-parse --show-toplevel"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)

    (stdout, stderr) = proc.communicate()

    # If there was no error return the output
    if not stderr:
        logger.addEvent('using_git')
        return stdout

    proc = subprocess.Popen(["hg root"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)

    (stdout, stderr) = proc.communicate()

    # If there was no error return the output
    if not stderr:
        logger.addEvent('using_hg')
        return stdout

    # Not a git or hg repo, go with ~/www as a default
    logger.addEvent('used_outside_repo')
    return './'


PREPEND_PATH = getRepoPath().strip() + '/'


# returns a filename and (optional) line number
# if it matches
def matchLine(line):
    # Homedirs need a separate regex. TODO -- fix this copypasta
    matches = HOMEDIR_REGEX.search(line)
    if matches:
        groups = matches.groups()
        file = groups[0]
        num = 0 if groups[2] is None else int(groups[2])
        return (file, num, matches)

    matches = MASTER_REGEX.search(line)
    # the master regex matches tbgs results with
    # line numbers, so we prefer that and test it first
    if matches:
        groups = matches.groups()
        file = groups[0]
        num = 0 if groups[2] is None else int(groups[2])
        # one real quick check -- did we find a better match
        # earlier in the regex?
        other_matches = OTHER_BGS_RESULT_REGEX.search(line)
        if not other_matches:
            return (file, num, matches)
        if other_matches.start() >= matches.start():
            # return as before
            return (file, num, matches)
        # we actually want the BGS result, not the one after
        groups = other_matches.groups()
        return (groups[0], int(groups[2]), other_matches)

    # if something clearly looks like an *bgs result but
    # just has a weird filename (like all caps with no extension)
    # then we can match that as well. Note that we require
    # the line number match since otherwise this would be too lax
    # of a regex.
    matches = OTHER_BGS_RESULT_REGEX.search(line)
    if matches:
        groups = matches.groups()
        file = groups[0]
        num = 0 if groups[2] is None else int(groups[2])
        return (file, num, matches)

    # ok maybe its just a normal file (with a dot)
    # so lets test for that if the above fails
    matches = JUST_FILE.search(line)
    if matches:
        file = matches.groups()[0]
        return (file, 0, matches)

    # ok finally it might be a file with no periods. we test
    # this last since its more restrictive, because we dont
    # want to match things like cx('foo/root'). hence
    # we require some minimum number of slashes and minimum
    # file name length
    matches = FILE_NO_PERIODS.search(line)
    if not matches:
        return None
    file = matches.groups()[0]
    return (file, 0, matches)


def prependDir(file):
    if not file or len(file) < 2:
        return file

    if file[0] == '/':
        return file

    if file[0:2] == '~/':
        # need to absolute it
        return os.path.expanduser(file)

    # if it starts with ./ (grep), then that's the easiest because abspath
    # will resolve this
    if file[0:2] in ['./', '..', '~/']:
        return file

    # some peeps do forcedir and expand the path beforehand,
    # so lets check for that case here
    first = file.split(os.sep)[0]
    if first == 'home':
        # already absolute, easy
        return '/' + file

    if first in REPOS:
        return '~/' + file

    if '/' not in file:
        # assume current dir like ./
        return './' + file

    # git show has a/stuff and b/stuff
    if file[0:2] == 'a/' or file[0:2] == 'b/':
        return PREPEND_PATH + file[2:]

    splitUp = file.split('/')
    if splitUp[0] == 'www':
        return PREPEND_PATH + '/'.join(splitUp[1:])

    # hope
    return PREPEND_PATH + '/'.join(splitUp)
