# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

KEY_BINDINGS_FOR_TEST_CONFIG_CONTENT = "[bindings]\nr = rspec\ns = subl\n"


class KeyBindingsForTest(object):

    bindings = [('r', 'rspec'.encode('utf-8')), ('s', 'subl'.encode('utf-8'))]
