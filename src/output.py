# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
import os
import pickle
import re

import logger
import stateFiles

DEBUG = '~/.fbPager.debug.text'
RED_COLOR = u'\033[0;31m'
NO_COLOR = u'\033[0m'

INVALID_FILE_WARNING = '''
Warning! Some invalid or unresolvable files were detected.
'''

GIT_ABBREVIATION_WARNING = '''
It looks like one of these is a git abbreviated file with
a triple dot path (.../). Try to turn off git's abbreviation
with --numstat so we get actual paths (not abbreviated
versions which cannot be resolved.
'''

CONTINUE_WARNING = 'Are you sure you want to continue? Ctrl-C to quit'


# The two main entry points into this module:
#


def execComposedCommand(command, lineObjs):
    if not len(command):
        editFiles(lineObjs)
        return
    logger.addEvent('command_on_num_files', len(lineObjs))
    command = composeCommand(command, lineObjs)
    appendAliasExpansion()
    appendIfInvalid(lineObjs)
    appendFriendlyCommand(command)
    appendExit()


def editFiles(lineObjs):
    logger.addEvent('editing_num_files', len(lineObjs))
    filesAndLineNumbers = [(lineObj.getPath(), lineObj.getLineNum())
                           for lineObj in lineObjs]
    command = joinFilesIntoCommand(filesAndLineNumbers)
    appendIfInvalid(lineObjs)
    appendToFile(command)
    appendExit()


# Private helpers
def appendIfInvalid(lineObjs):
    # lastly lets check validity and actually output an
    # error if any files are invalid
    invalidLines = [line for line in lineObjs if not line.isResolvable()]
    if not invalidLines:
        return
    appendError(INVALID_FILE_WARNING)
    if len([line for line in invalidLines if line.isGitAbbreviatedPath()]):
        appendError(GIT_ABBREVIATION_WARNING)
    appendToFile('read -p "%s" -r' % CONTINUE_WARNING)


def debug(*args):
    for arg in args:
        appendToFile('echo "DEBUG: ' + str(arg) + '"')


def outputSelection(lineObjs):
    filePath = stateFiles.getSelectionFilePath()
    indices = [l.index for l in lineObjs]
    file = open(filePath, 'wb')
    pickle.dump(indices, file)
    file.close()


def getEditorAndPath():
    editor_path = os.environ.get('FPP_EDITOR') or os.environ.get('VISUAL') or \
        os.environ.get('EDITOR')
    if editor_path:
        editor = os.path.basename(editor_path)
        logger.addEvent('using_editor_' + editor)
        return editor, editor_path
    return 'vim', 'vim'


def expandPath(filePath):
    # expand ~/ paths
    filePath = os.path.expanduser(filePath)
    # and in case of grep, expand ./ as well
    return os.path.abspath(filePath)


def joinFilesIntoCommand(filesAndLineNumbers):
    editor, editor_path = getEditorAndPath()
    cmd = editor_path + ' '
    if editor == 'vim -p':
        firstFilePath, firstLineNum = filesAndLineNumbers[0]
        cmd += ' +%d %s' % (firstLineNum, firstFilePath)
        for (filePath, lineNum) in filesAndLineNumbers[1:]:
            cmd += ' +"tabnew +%d %s"' % (lineNum, filePath)
    elif editor in ['vim', 'mvim'] and not os.environ.get('FPP_DISABLE_SPLIT'):
        firstFilePath, firstLineNum = filesAndLineNumbers[0]
        cmd += ' +%d %s' % (firstLineNum, firstFilePath)
        for (filePath, lineNum) in filesAndLineNumbers[1:]:
            cmd += ' +"vsp +%d %s"' % (lineNum, filePath)
    else:
        for (filePath, lineNum) in filesAndLineNumbers:
            if editor in ['vi', 'nvim', 'nano', 'joe', 'emacs',
                          'emacsclient'] and lineNum != 0:
                cmd += ' +%d \'%s\'' % (lineNum, filePath)
            elif editor in ['subl', 'sublime', 'atom'] and lineNum != 0:
                cmd += ' \'%s:%d\'' % (filePath, lineNum)
            else:
                cmd += " '%s'" % filePath
    return cmd


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
    command = command.decode('utf-8')
    paths = ["'%s'" % lineObj.getPath() for lineObj in lineObjs]
    path_str = ' '.join(paths)
    if '$F' in command:
        command = command.replace('$F', path_str)
    else:
        command = command + ' ' + path_str
    return command


def outputNothing():
    appendToFile('echo "nothing to do!"; exit 1')


def clearFile():
    writeToFile('')


def appendAliasExpansion():
    # zsh by default expands aliases when running in interactive mode
    # (see ../fpp). bash (on this author's Yosemite box) seems to have
    # alias expansion off when run with -i present and -c absent,
    # despite documentation hinting otherwise.
    #
    # so here we must ask bash to turn on alias expansion.
    shell = os.environ.get('SHELL')
    if 'fish' not in shell:
        appendToFile("""
if type shopt > /dev/null; then
  shopt -s expand_aliases
fi
""")


def appendFriendlyCommand(command):
    header = 'echo "executing command:"\n' + \
             'echo "' + command.replace('"', '\\"') + '"'
    appendToFile(header)
    appendToFile(command)


def appendError(text):
    appendToFile('printf "%s%s%s\n"' % (RED_COLOR, text, NO_COLOR))


def appendToFile(command):
    file = open(stateFiles.getScriptOutputFilePath(), 'a')
    file.write(command + '\n')
    file.close()
    logger.output()


def appendExit():
    # The `$SHELL` environment variable points to the default shell,
    # not the current shell. But they are often the same. And there
    # is no other simple and reliable way to detect the current shell.
    shell = os.environ['SHELL']
    # ``csh``, fish`` and, ``rc`` uses ``$status`` instead of ``$?``.
    if shell.endswith('csh') or shell.endswith('fish') or shell.endswith('rc'):
        exit_status = '$status'
    # Otherwise we assume a Bournal-like shell, e.g. bash and zsh.
    else:
        exit_status = '$?'
    appendToFile('exit {status};'.format(status=exit_status))


def writeToFile(command):
    file = open(stateFiles.getScriptOutputFilePath(), 'w')
    file.write(command + '\n')
    file.close()
    logger.output()
