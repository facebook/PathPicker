# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
KEY_BINDINGS_FOR_TEST_CONFIG_CONTENT = "[bindings]\nr = rspec\ns = subl\n"


class KeyBindingsForTest(object):

    bindings = [('r', 'rspec'.encode('utf-8')), ('s', 'subl'.encode('utf-8'))]
