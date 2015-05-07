# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# @nolint
import os
import pickle
import re

import logger

OUTPUT_FILE = '~/.fbPager.sh'
SELECTION_PICKLE = '~/.fbPager.selection.pickle'
BASH_RC = '~/.bashrc'
DEBUG = '~/.fbPager.debug.text'

ALIAS_REGEX = re.compile('alias (\w+)=[\'"](.*?)[\'"]')


def debug(*args):
    for arg in args:
        appendToFile('echo "DEBUG: ' + str(arg) + '"')


def outputSelection(lineObjs):
    filePath = os.path.expanduser(SELECTION_PICKLE)
    indices = [l.index for l in lineObjs]
    pickle.dump(indices, open(filePath, 'w'))


def getEditorAndPath():
    editor_path = os.environ.get('EDITOR')
    if editor_path:
        editor = os.path.basename(editor_path)
        logger.addEvent('using_editor_' + editor)
        return editor, editor_path
    return 'vim', 'vim'


def getEditFileCommand(filePath, lineNum):
    editor, _editor_path = getEditorAndPath()
    if editor == 'vim' and lineNum != 0:
        return '\'%s\' +%d' % (filePath, lineNum)
    elif editor in ['joe', 'emacs'] and lineNum != 0:
        return '+%d \'%s\'' % (lineNum, filePath)
    else:
        return "'%s'" % filePath


def getAliases():
    try:
        lines = open(os.path.expanduser(BASH_RC), 'r').readlines()
    except IOError:
        return {}
    pairs = []
    for line in lines:
        results = ALIAS_REGEX.search(line)
        if results:
            # groups is a tuple of (word, expanded)
            pairs.append(results.groups())
    # ok now we can make a dict out of this
    return dict(pairs)


def expandAliases(command):
    aliasToExpand = getAliases()
    tokens = command.split(' ')
    if (tokens[0] in aliasToExpand):
        tokens[0] = aliasToExpand[tokens[0]]
    return ' '.join(tokens)


def expandPath(filePath):
    # expand ~/ paths
    filePath = os.path.expanduser(filePath)
    # and in case of grep, expand ./ as well
    return os.path.abspath(filePath)


def joinEditCommands(partialCommands):
    editor, editor_path = getEditorAndPath()
    if editor == 'vim':
        if len(partialCommands) > 1:
            return editor_path + ' -O ' + ' '.join(partialCommands)
        else:
            return editor_path + ' ' + partialCommands[0]
    # Assume that all other editors behave like emacs
    return editor_path + ' ' + ' '.join(partialCommands)


def editFiles(lineObjs):
    partialCommands = []
    logger.addEvent('editing_num_files', len(lineObjs))
    for lineObj in lineObjs:
        (file, num) = (lineObj.getFile(), lineObj.getLineNum())
        partialCommands.append(getEditFileCommand(file, num))
    command = joinEditCommands(partialCommands)
    appendToFile(command)


def composeCdCommand(command, lineObjs):
    filePath = os.path.expanduser(lineObjs[0].getDir())
    filePath = os.path.abspath(filePath)
    # now copy it into clipboard for cdp-ing
    # TODO -- this is pretty specific to
    # pcottles workflow
    command = 'echo "' + filePath + '" > ~/.dircopy'
    return command


def isCdCommand(command):
    return command[0:3] in ['cd ', 'cd']


def composeCommand(command, lineObjs):
    if isCdCommand(command):
        return composeCdCommand(command, lineObjs)
    else:
        return composeFileCommand(command, lineObjs)


def composeFileCommand(command, lineObjs):
    files = ["'%s'" % lineObj.getFile() for lineObj in lineObjs]
    file_str = ' '.join(files)
    if '$F' in command:
        command = command.replace('$F', file_str)
    else:
        command = command + ' ' + file_str
    return command


def execComposedCommand(command, lineObjs):
    if not len(command):
        editFiles(lineObjs)
        return
    logger.addEvent('command_on_num_files', len(lineObjs))
    command = composeCommand(command, lineObjs)
    command = expandAliases(command)
    writeFriendlyCommand(command)


def outputNothing():
    appendToFile('echo "nothing to do!"')


def clearFile():
    writeToFile('')


def writeFriendlyCommand(command):
    header = 'echo "executing command:"\n' + \
    'echo "' + command.replace('"', '\\"') + '"'
    appendToFile(header)
    appendToFile(command)


def appendToFile(command):
    file = open(os.path.expanduser(OUTPUT_FILE), 'a')
    file.write(command + '\n')
    file.close()
    logger.output()


def writeToFile(command):
    file = open(os.path.expanduser(OUTPUT_FILE), 'w')
    file.write(command + '\n')
    file.close()
    logger.output()
