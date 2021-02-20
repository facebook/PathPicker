# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Tuple

from pathpicker.char_code_mapping import CHAR_TO_CODE

ATTRIBUTE_SYMBOL_MAPPING = {
    0: " ",
    1: " ",
    2: "B",
    2097154: "*",  # bold white
    131072: "_",
    3: "G",
    4: "R",
    5: "?",
    6: "!",
    2097153: "W",
    2097155: "|",  # bold
    2097156: "/",  # bold
    2097158: "~",  # bold
    2097157: "@",  # bold
    7: "?",
}


class ScreenForTest:

    """A dummy object that is dependency-injected in place
    of curses standard screen. Allows us to unit-test parts
    of the UI code"""

    def __init__(self, char_inputs, max_x, max_y):
        self.max_x = max_x
        self.max_y = max_y
        self.cursor_x = 0
        self.cursor_y = 0
        self.output = {}
        self.past_screens = []
        self.char_inputs = char_inputs
        self.erase()
        self.current_attribute = 0

    def getmaxyx(self):
        return self.max_y, self.max_x

    def refresh(self):
        if self.contains_content(self.output):
            # we have an old screen, so add it
            self.past_screens.append(dict(self.output))

    def contains_content(self, screen):
        for _coord, pair in screen.items():
            (char, _attr) = pair
            if char:
                return True
        return False

    def erase(self):
        self.output = {}
        for x in range(self.max_x):
            for y in range(self.max_y):
                coord = (x, y)
                self.output[coord] = ("", 1)

    def move(self, y_pos, x_pos):
        self.cursor_y = y_pos
        self.cursor_x = x_pos

    def attrset(self, attr):
        self.current_attribute = attr

    def addstr(self, y_pos, x_pos, string, attr=None):
        if attr:
            self.attrset(attr)
        for deltaX, value in enumerate(string):
            coord = (x_pos + deltaX, y_pos)
            self.output[coord] = (value, self.current_attribute)

    def delch(self, y_pos, x_pos):
        """Delete a character. We implement this by removing the output,
        NOT by printing a space"""
        self.output[(x_pos, y_pos)] = ("", 1)

    def getch(self):
        return CHAR_TO_CODE[self.char_inputs.pop(0)]

    def getstr(self, _y, _x, _max_len) -> str:
        # TODO -- enable editing this
        return ""

    def print_screen(self):
        for index, row in enumerate(self.get_rows()):
            print("Row %02d:%s" % (index, row))

    def print_old_screens(self):
        for oldScreen in range(self.get_num_past_screens()):
            for index, row in enumerate(self.get_rows_for_past_screen(oldScreen)):
                print("Screen %02d Row %02d:%s" % (oldScreen, index, row))

    def get_num_past_screens(self):
        return len(self.past_screens)

    def get_rows_for_past_screen(self, past_screen):
        return self.get_rows(screen=self.past_screens[past_screen])

    def get_rows_with_attributes_for_past_screen(self, past_screen):
        return self.get_rows_with_attributes(screen=self.past_screens[past_screen])

    def get_rows_with_attributes_for_past_screens(self, past_screens):
        """Get the rows & attributes for the array of screens as one stream
        (there is no extra new line or extra space between pages)"""
        pages = map(
            lambda screen_index: self.get_rows_with_attributes(
                screen=self.past_screens[screen_index]
            ),
            past_screens,
        )

        # join the pages together into one stream
        lines, attributes = zip(*pages)
        return (
            [line for page in lines for line in page],
            [line for page in attributes for line in page],
        )

    def get_rows_with_attributes(self, screen=None) -> Tuple:
        if not screen:
            screen = self.output

        rows = []
        attribute_rows = []
        for y in range(self.max_y):
            row = ""
            attribute_row = ""
            for x in range(self.max_x):
                coord = (x, y)
                (char, attr) = screen[coord]
                row += char
                attribute_row += self.get_attribute_symbol_for_code(attr)
            rows.append(row)
            attribute_rows.append(attribute_row)
        return rows, attribute_rows

    def get_rows(self, screen=None):
        (rows, _) = self.get_rows_with_attributes(screen)
        return rows

    def get_attribute_symbol_for_code(self, code):
        symbol = ATTRIBUTE_SYMBOL_MAPPING.get(code, None)
        if symbol is None:
            raise ValueError("%d not mapped" % code)
        return symbol
