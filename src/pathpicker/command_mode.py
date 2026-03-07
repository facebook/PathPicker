# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import subprocess


def expand_tokens(cmd: str, file_path: str) -> str:
    """
    Replace custom tokens in command string.
    $FILE -> full file path
    $DIR -> directory of file
    $BASENAME -> file name without path
    """
    return (
        cmd.replace("$FILE", file_path)
           .replace("$DIR", os.path.dirname(file_path))
           .replace("$BASENAME", os.path.basename(file_path))
    )


def run_command(cmd: str, file_path: str, auto_mode: bool = False) -> None:
    """
    Runs a command safely with token expansion.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Error: file {file_path} does not exist!")
        return

    cmd_to_run = expand_tokens(cmd, file_path)

    if not auto_mode:
        confirm = input(f"Run command '{cmd_to_run}'? [y/N] ")
        if confirm.lower() != "y":
            print("Command skipped.")
            return

    try:
        subprocess.run(cmd_to_run, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")