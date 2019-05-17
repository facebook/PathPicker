# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import print_function

import curses

CODE_TO_CHAR = dict((i, chr(i)) for i in range(256))
CODE_TO_CHAR.update((value, name[4:]) for name, value in vars(curses).items()
                    if name.startswith('KEY_'))
# special exceptions
CODE_TO_CHAR[10] = 'ENTER'

CHAR_TO_CODE = dict((v, k) for k, v in CODE_TO_CHAR.items())
