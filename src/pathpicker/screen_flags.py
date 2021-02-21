# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import argparse
from typing import List


class ScreenFlags:

    """A class that just represents the total set of flags
    available to FPP. Note that some of these are actually
    processed by the fpp batch file, and not by python.
    However, they are documented here because argsparse is
    clean and easy to use for that purpose.

    The flags that are actually processed and are meaningful
    are

    * c (command)
    * r (record)

    """

    def __init__(self, args: argparse.Namespace):
        self.args = args

    def get_preset_command(self) -> str:
        return " ".join(self.args.command)

    def get_execute_keys(self) -> List[str]:
        return list(self.args.execute_keys)

    def get_is_clean_mode(self) -> bool:
        return bool(self.args.clean)

    def get_disable_file_checks(self) -> bool:
        return bool(self.args.no_file_checks) or bool(self.args.all_input)

    def get_all_input(self) -> bool:
        return bool(self.args.all_input)

    @staticmethod
    def get_arg_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="fpp")
        parser.add_argument(
            "-r",
            "--record",
            help="""
Record input and output. This is
largely used for testing, but you may find it useful for scripting.""",
            default=False,
            action="store_true",
        )
        parser.add_argument(
            "--version",
            default=False,
            help="""
Print the version of fpp and exit.""",
            action="store_true",
        )
        parser.add_argument(
            "--clean",
            default=False,
            action="store_true",
            help="""
Remove the state files that fpp uses when starting up, including
the previous input used and selection pickle. Useful when using fpp
in a script context where the previous state should be discarded.""",
        )
        parser.add_argument(
            "-ko",
            "--keep-open",
            default=False,
            action="store_true",
            help="""keep PathPicker open once
a file selection or command is performed. This will loop the program
until Ctrl-C is used to terminate the process.""",
        )
        parser.add_argument(
            "-c",
            "--command",
            help="""You may specify a command while
invoking fpp that will be run once files have been selected. Normally,
fpp opens your editor (see discussion of $EDITOR, $VISUAL, and
$FPP_EDITOR) when you press enter. If you specify a command here,
it will be invoked instead.""",
            default="",
            action="store",
            nargs="+",
        )

        parser.add_argument(
            "-e",
            "--execute-keys",
            help="""Automatically execute the given keys when
the file list shows up.
This is useful on certain cases, e.g. using "END" in order to automatically
go to the last entry when there is a long list.""",
            default="",
            action="store",
            nargs="+",
        )
        parser.add_argument(
            "-nfc",
            "--no-file-checks",
            default=False,
            action="store_true",
            help="""You may want to turn off file
system validation for a particular instance of PathPicker; this flag
disables our internal logic for checking if a regex match is an actual file
on the system. This is particularly useful when using PathPicker for an input
of, say, deleted files in git status that you would like to restore to a given
revision. It enables you to select the deleted files even though they
do not exist on the system anymore.""",
        )
        parser.add_argument(
            "-ai",
            "--all-input",
            default=False,
            action="store_true",
            help="""You may force PathPicker to recognize all
lines as acceptable input. Typically, PathPicker will scan the input for references
to file paths. Passing this option will disable those scans and the program will
assume that every input line is a match. In practice, this option allows for input
selection for a variety of sources that would otherwise be unsupported -- git branches,
mercurial bookmarks, etc.""",
        )
        parser.add_argument(
            "-ni",
            "--non-interactive",
            default=False,
            action="store_true",
            help="""Normally, the command that runs after you've
chosen files to operate on is spawned in an interactive subshell.  This allows you
to use aliases and have access to environment variables defined in your startup
files, but can have strange side-effects when starting and stopping jobs
and redirecting inputs.  Using this flag runs your commands in a non-interactive
subshell, like a normal shell script.""",
        )
        parser.add_argument(
            "-a",
            "--all",
            default=False,
            action="store_true",
            help="""Automatically select all available lines
once the interactive editor has been entered.""",
        )
        return parser

    @staticmethod
    def init_from_args(argv: List[str]) -> "ScreenFlags":
        (args, _chars) = ScreenFlags.get_arg_parser().parse_known_args(argv)
        return ScreenFlags(args)
