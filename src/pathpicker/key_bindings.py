# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import configparser
import os
from typing import List, NewType, Tuple

from pathpicker.state_files import FPP_DIR

KEY_BINDINGS_FILE = os.path.join(FPP_DIR, ".fpp.keys")


KeyBindings = NewType("KeyBindings", List[Tuple[str, str]])


def read_key_bindings(key_bindings_file: str = KEY_BINDINGS_FILE) -> KeyBindings:
    """Returns configured key bindings, in the format [(key, command), ...].
    The ordering of the entries is not guaranteed, although it's irrelevant
    to the purpose.
    """
    config_file_path = os.path.expanduser(key_bindings_file)
    parser = configparser.ConfigParser()
    parser.read(config_file_path)

    bindings = KeyBindings([])
    if parser.has_section("bindings"):
        bindings = KeyBindings(parser.items("bindings"))
    return bindings
