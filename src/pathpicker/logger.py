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


def writeToFile(content):
    file = open(state_files.getLoggerFilePath(), "w")
    file.write(content)
    file.close()


def clearFile():
    writeToFile("")


events = []


def addEvent(event, number=None):
    events.append((event, number))


def getLoggingDicts():
    unixname = getpass.getuser()
    dicts = []
    for (event, number) in events:
        dicts.append({"unixname": unixname, "num": number, "eventname": event})
    return dicts


def output():
    dicts = getLoggingDicts()
    json_output = json.dumps(dicts)
    writeToFile(json_output)
