# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import stat
from typing import List

FPP_DIR = os.environ.get("FPP_DIR") or "~/.cache/fpp"
PICKLE_FILE = ".pickle"
SELECTION_PICKLE = ".selection.pickle"
OUTPUT_FILE = ".fpp.sh"
LOGGER_FILE = ".fpp.log"


def assert_dir_created() -> None:
    path = os.path.expanduser(FPP_DIR)
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def get_pickle_file_path() -> str:
    assert_dir_created()
    return os.path.expanduser(os.path.join(FPP_DIR, PICKLE_FILE))


def get_selection_file_path() -> str:
    assert_dir_created()
    return os.path.expanduser(os.path.join(FPP_DIR, SELECTION_PICKLE))


def get_script_output_file_path() -> str:
    assert_dir_created()
    return os.path.expanduser(os.path.join(FPP_DIR, OUTPUT_FILE))


def get_logger_file_path() -> str:
    assert_dir_created()
    return os.path.expanduser(os.path.join(FPP_DIR, LOGGER_FILE))


def is_state_file_safe(path: str) -> bool:
    """
    Basic safety checks before unpickling:
      - file must exist and be owned by current uid
      - not group/world-writable
    """
    try:
        st = os.stat(path)
    except OSError:
        return False
    if st.st_uid != os.getuid():
        return False
    if st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        return False
    return True


def get_all_state_files() -> List[str]:
    # keep this update to date! We do not include
    # the script output path since that gets cleaned automatically
    return [
        get_pickle_file_path(),
        get_selection_file_path(),
        get_logger_file_path(),
        get_script_output_file_path(),
    ]
