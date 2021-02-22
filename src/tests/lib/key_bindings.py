# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathpicker.key_bindings import KeyBindings

KEY_BINDINGS_FOR_TEST_CONFIG_CONTENT: str = "[bindings]\nr = rspec\ns = subl\n"
KEY_BINDINGS_FOR_TEST: KeyBindings = KeyBindings(
    [
        ("r", "rspec"),
        ("s", "subl"),
    ]
)
