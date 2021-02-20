# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import getpass
import json

from pathpicker import state_files

# This file just outputs some simple log events that are consumed by
# another service for internal logging at Facebook. Use it if you want
# to, or disable it if you want.


def write_to_file(content):
    file = open(state_files.get_logger_file_path(), "w")
    file.write(content)
    file.close()


def clear_file():
    write_to_file("")


events = []


def add_event(event, number=None):
    events.append((event, number))


def get_logging_dicts():
    unixname = getpass.getuser()
    dicts = []
    for (event, number) in events:
        dicts.append({"unixname": unixname, "num": number, "eventname": event})
    return dicts


def output():
    dicts = get_logging_dicts()
    json_output = json.dumps(dicts)
    write_to_file(json_output)
