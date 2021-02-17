# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import pickle

from pathpicker import logger, state_files

DEBUG = "~/.fbPager.debug.text"
RED_COLOR = u"\033[0;31m"
NO_COLOR = u"\033[0m"

INVALID_FILE_WARNING = """
Warning! Some invalid or unresolvable files were detected.
"""

GIT_ABBREVIATION_WARNING = """
It looks like one of these is a git abbreviated file with
a triple dot path (.../). Try to turn off git's abbreviation
with --numstat so we get actual paths (not abbreviated
versions which cannot be resolved.
"""

CONTINUE_WARNING = "Are you sure you want to continue? Ctrl-C to quit"


# The two main entry points into this module:
#


def execComposedCommand(command, lineObjs):
    if not len(command):
        editFiles(lineObjs)
        return

    if not isinstance(command, str):
        command = command.decode()

    logger.addEvent("command_on_num_files", len(lineObjs))
    command = composeCommand(command, lineObjs)
    appendAliasExpansion()
    appendIfInvalid(lineObjs)
    appendFriendlyCommand(command)
    appendExit()


def editFiles(lineObjs):
    logger.addEvent("editing_num_files", len(lineObjs))
    filesAndLineNumbers = [
        (lineObj.getPath(), lineObj.getLineNum()) for lineObj in lineObjs
    ]
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
    filePath = state_files.getSelectionFilePath()
    indices = [line.index for line in lineObjs]
    file = open(filePath, "wb")
    pickle.dump(indices, file)
    file.close()


def getEditorAndPath():
    editor_path = (
        os.environ.get("FPP_EDITOR")
        or os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
    )
    if editor_path:
        editor = os.path.basename(editor_path)
        logger.addEvent("using_editor_" + editor)
        return editor, editor_path
    return "vim", "vim"


def expandPath(filePath):
    # expand ~/ paths
    filePath = os.path.expanduser(filePath)
    # and in case of grep, expand ./ as well
    return os.path.abspath(filePath)


def joinFilesIntoCommand(filesAndLineNumbers):
    editor, editor_path = getEditorAndPath()
    cmd = editor_path + " "
    if editor == "vim -p":
        firstFilePath, firstLineNum = filesAndLineNumbers[0]
        cmd += " +%d %s" % (firstLineNum, firstFilePath)
        for (filePath, lineNum) in filesAndLineNumbers[1:]:
            cmd += ' +"tabnew +%d %s"' % (lineNum, filePath)
    elif editor in ["vim", "mvim", "nvim"] and not os.environ.get("FPP_DISABLE_SPLIT"):
        firstFilePath, firstLineNum = filesAndLineNumbers[0]
        cmd += " +%d %s" % (firstLineNum, firstFilePath)
        for (filePath, lineNum) in filesAndLineNumbers[1:]:
            cmd += ' +"vsp +%d %s"' % (lineNum, filePath)
    else:
        for (filePath, lineNum) in filesAndLineNumbers:
            editor_without_args = editor.split()[0]
            if (
                editor_without_args
                in ["vi", "nvim", "nano", "joe", "emacs", "emacsclient"]
                and lineNum != 0
            ):
                cmd += " +%d '%s'" % (lineNum, filePath)
            elif editor_without_args in ["subl", "sublime", "atom"] and lineNum != 0:
                cmd += " '%s:%d'" % (filePath, lineNum)
            elif lineNum != 0 and os.environ.get("FPP_LINENUM_SEP"):
                cmd += " '%s%s%d'" % (
                    filePath,
                    os.environ.get("FPP_LINENUM_SEP"),
                    lineNum,
                )
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
    return command[0:3] in ["cd ", "cd"]


def composeCommand(command, lineObjs):
    if isCdCommand(command):
        return composeCdCommand(command, lineObjs)
    else:
        return composeFileCommand(command, lineObjs)


def composeFileCommand(command, lineObjs):
    command = command.encode().decode("utf-8")
    paths = ["'%s'" % lineObj.getPath() for lineObj in lineObjs]
    path_str = " ".join(paths)
    if "$F" in command:
        command = command.replace("$F", path_str)
    else:
        command = command + " " + path_str
    return command


def outputNothing():
    appendToFile('echo "nothing to do!"; exit 1')


def clearFile():
    writeToFile("")


def appendAliasExpansion():
    # zsh by default expands aliases when running in interactive mode
    # (see ../fpp). bash (on this author's Yosemite box) seems to have
    # alias expansion off when run with -i present and -c absent,
    # despite documentation hinting otherwise.
    #
    # so here we must ask bash to turn on alias expansion.
    shell = os.environ.get("SHELL")
    if shell is None or "fish" not in shell:
        appendToFile(
            """
if type shopt > /dev/null; then
  shopt -s expand_aliases
fi
"""
        )


def appendFriendlyCommand(command):
    header = (
        'echo "executing command:"\n' + 'echo "' + command.replace('"', '\\"') + '"'
    )
    appendToFile(header)
    appendToFile(command)


def appendError(text):
    appendToFile('printf "%s%s%s\n"' % (RED_COLOR, text, NO_COLOR))


def appendToFile(command):
    file = open(state_files.getScriptOutputFilePath(), "a")
    file.write(command + "\n")
    file.close()
    logger.output()


def appendExit():
    # The `$SHELL` environment variable points to the default shell,
    # not the current shell. But they are often the same. And there
    # is no other simple and reliable way to detect the current shell.
    shell = os.environ["SHELL"]
    # ``csh``, fish`` and, ``rc`` uses ``$status`` instead of ``$?``.
    if shell.endswith("csh") or shell.endswith("fish") or shell.endswith("rc"):
        exit_status = "$status"
    # Otherwise we assume a Bournal-like shell, e.g. bash and zsh.
    else:
        exit_status = "$?"
    appendToFile("exit {status};".format(status=exit_status))


def writeToFile(command):
    file = open(state_files.getScriptOutputFilePath(), "w")
    file.write(command + "\n")
    file.close()
    logger.output()
