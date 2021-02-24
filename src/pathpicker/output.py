# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import pickle
from typing import List, Tuple

from pathpicker import logger, state_files
from pathpicker.line_format import LineMatch

RED_COLOR = "\033[0;31m"
NO_COLOR = "\033[0m"

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


def exec_composed_command(command: str, line_objs: List[LineMatch]) -> None:
    if not command:
        edit_files(line_objs)
        return

    logger.add_event("command_on_num_files", len(line_objs))
    command = compose_command(command, line_objs)
    append_alias_expansion()
    append_if_invalid(line_objs)
    append_friendly_command(command)
    append_exit()


def edit_files(line_objs: List[LineMatch]) -> None:
    logger.add_event("editing_num_files", len(line_objs))
    files_and_line_numbers = [
        (line_obj.get_path(), line_obj.get_line_num()) for line_obj in line_objs
    ]
    command = join_files_into_command(files_and_line_numbers)
    append_if_invalid(line_objs)
    append_to_file(command)
    append_exit()


# Private helpers
def append_if_invalid(line_objs: List[LineMatch]) -> None:
    # lastly lets check validity and actually output an
    # error if any files are invalid
    invalid_lines = [line for line in line_objs if not line.is_resolvable()]
    if not invalid_lines:
        return
    append_error(INVALID_FILE_WARNING)
    if any(map(LineMatch.is_git_abbreviated_path, invalid_lines)):
        append_error(GIT_ABBREVIATION_WARNING)
    append_to_file(f'read -p "{CONTINUE_WARNING}" -r')


def output_selection(line_objs: List[LineMatch]) -> None:
    file_path = state_files.get_selection_file_path()
    indices = [line.index for line in line_objs]
    file = open(file_path, "wb")
    pickle.dump(indices, file)
    file.close()


def get_editor_and_path() -> Tuple[str, str]:
    editor_path = (
        os.environ.get("FPP_EDITOR")
        or os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
    )
    if editor_path:
        editor = os.path.basename(editor_path)
        logger.add_event(f"using_editor_{editor}")
        return editor, editor_path
    return "vim", "vim"


def join_files_into_command(files_and_line_numbers: List[Tuple[str, int]]) -> str:
    editor, editor_path = get_editor_and_path()
    cmd = editor_path + " "
    if editor == "vim -p":
        first_file_path, first_line_num = files_and_line_numbers[0]
        cmd += f" +{first_line_num} {first_file_path}"
        for (file_path, line_num) in files_and_line_numbers[1:]:
            cmd += f' +"tabnew +{line_num} {file_path}"'
    elif editor in ["vim", "mvim", "nvim"] and not os.environ.get("FPP_DISABLE_SPLIT"):
        first_file_path, first_line_num = files_and_line_numbers[0]
        cmd += f" +{first_line_num} {first_file_path}"
        for (file_path, line_num) in files_and_line_numbers[1:]:
            cmd += f' +"vsp +{line_num} {file_path}"'
    else:
        for (file_path, line_num) in files_and_line_numbers:
            editor_without_args = editor.split()[0]
            if (
                editor_without_args
                in ["vi", "nvim", "nano", "joe", "emacs", "emacsclient", "micro"]
                and line_num != 0
            ):
                cmd += f" +{line_num} '{file_path}'"
            elif editor_without_args in ["subl", "sublime", "atom"] and line_num != 0:
                cmd += f" '{file_path}:{line_num}'"
            elif line_num != 0 and os.environ.get("FPP_LINENUM_SEP"):
                cmd += f" '{file_path}{os.environ.get('FPP_LINENUM_SEP')}{line_num}'"
            else:
                cmd += f" '{file_path}'"
    return cmd


def compose_cd_command(_command: str, line_objs: List[LineMatch]) -> str:
    file_path = os.path.expanduser(line_objs[0].get_dir())
    file_path = os.path.abspath(file_path)
    # now copy it into clipboard for cdp-ing
    # TODO -- this is pretty specific to
    # pcottles workflow
    return f'echo "{file_path}" > ~/.dircopy'


def is_cd_command(command: str) -> bool:
    return command[0:3] in ["cd ", "cd"]


def compose_command(command: str, line_objs: List[LineMatch]) -> str:
    if is_cd_command(command):
        return compose_cd_command(command, line_objs)
    return compose_file_command(command, line_objs)


def compose_file_command(command: str, line_objs: List[LineMatch]) -> str:
    command = command.encode().decode("utf-8")
    paths = [f"'{line_obj.get_path()}'" for line_obj in line_objs]
    path_str = " ".join(paths)
    if "$F" in command:
        command = command.replace("$F", path_str)
    else:
        command = f"{command} {path_str}"
    return command


def output_nothing() -> None:
    append_to_file('echo "nothing to do!"; exit 1')


def clear_file() -> None:
    write_to_file("")


def append_alias_expansion() -> None:
    # zsh by default expands aliases when running in interactive mode
    # (see ../fpp). bash (on this author's Yosemite box) seems to have
    # alias expansion off when run with -i present and -c absent,
    # despite documentation hinting otherwise.
    #
    # so here we must ask bash to turn on alias expansion.
    shell = os.environ.get("SHELL")
    if shell is None or "fish" not in shell:
        append_to_file(
            """
if type shopt > /dev/null; then
  shopt -s expand_aliases
fi
"""
        )


def append_friendly_command(command: str) -> None:
    header = 'echo "executing command:"\necho "' + command.replace('"', '\\"') + '"'
    append_to_file(header)
    append_to_file(command)


def append_error(text: str) -> None:
    append_to_file(f'printf "{RED_COLOR}{text}{NO_COLOR}\n"')


def append_to_file(command: str) -> None:
    file = open(state_files.get_script_output_file_path(), "a")
    file.write(command + "\n")
    file.close()
    logger.output()


def append_exit() -> None:
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
    append_to_file(f"exit {exit_status};")


def write_to_file(command: str) -> None:
    file = open(state_files.get_script_output_file_path(), "w")
    file.write(command + "\n")
    file.close()
    logger.output()
