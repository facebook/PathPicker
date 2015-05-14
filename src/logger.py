# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
import json
import subprocess
import os

import stateFiles

# This file just outputs some simple log events that are consumed by
# another service for internal logging at Facebook. Use it if you want
# to, or disable it if you want.


def writeToFile(content):
    file = open(stateFiles.getLoggerFilePath(), 'w')
    file.write(content)
    file.close()


def clearFile():
    writeToFile('')


def getUnixName():
    proc = subprocess.Popen(['whoami'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)

    (stdout, stderr) = proc.communicate()
    if not stdout:
        return 'unknown'
    return stdout.replace('\n', '')


events = []


def addEvent(event, number=None):
    events.append((event, number))


def getLoggingDicts():
    unixname = getUnixName()
    dicts = []
    for (event, number) in events:
        dicts.append({'unixname': unixname, 'num': number, 'eventname': event})
    return dicts


def output():
    dicts = getLoggingDicts()
    output = json.dumps(dicts)
    writeToFile(output)
