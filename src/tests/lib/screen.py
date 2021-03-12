# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from copy import copy
from typing import Dict, List, NewType, Optional, Tuple

from pathpicker.char_code_mapping import CHAR_TO_CODE
from pathpicker.screen import ScreenBase

ATTRIBUTE_SYMBOL_MAPPING: Dict[int, str] = {
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


ScreenType = NewType("ScreenType", Dict[Tuple[int, int], Tuple[str, int]])


class ScreenForTest(ScreenBase):
    """A dummy object that is dependency-injected in place
    of curses standard screen. Allows us to unit-test parts
    of the UI code"""

    def __init__(self, char_inputs: List[str], max_x: int, max_y: int):
        self.max_x = max_x
        self.max_y = max_y
        self.output = ScreenType({})
        self.past_screens: List[ScreenType] = []
        self.char_inputs = char_inputs
        self.erase()
        self.current_attribute = 0

    def getmaxyx(self) -> Tuple[int, int]:
        return self.max_y, self.max_x

    def refresh(self) -> None:
        if self.contains_content(self.output):
            # we have an old screen, so add it
            self.past_screens.append(copy(self.output))

    def contains_content(self, screen: ScreenType) -> bool:
        for _coord, pair in screen.items():
            (char, _attr) = pair
            if char:
                return True
        return False

    def erase(self) -> None:
        self.output = ScreenType({})
        for x_pos in range(self.max_x):
            for y_pos in range(self.max_y):
                coord = (x_pos, y_pos)
                self.output[coord] = ("", 1)

    def move(self, _y_pos: int, _x_pos: int) -> None:
        pass

    def attrset(self, attr: int) -> None:
        self.current_attribute = attr

    def addstr(
        self, y_pos: int, x_pos: int, string: str, attr: Optional[int] = None
    ) -> None:
        if attr:
            self.attrset(attr)
        for delta_x, value in enumerate(string):
            coord = (x_pos + delta_x, y_pos)
            self.output[coord] = (value, self.current_attribute)

    def delch(self, y_pos: int, x_pos: int) -> None:
        """Delete a character. We implement this by removing the output,
        NOT by printing a space"""
        self.output[(x_pos, y_pos)] = ("", 1)

    def getch(self) -> int:
        return CHAR_TO_CODE[self.char_inputs.pop(0)]

    def getstr(self, _y: int, _x: int, _max_len: int) -> str:
        # TODO -- enable editing this
        return ""

    def print_screen(self) -> None:
        for index, row in enumerate(self.get_rows()):
            print(f"Row {index:02}:{row}")

    def print_old_screens(self) -> None:
        for old_screen in range(self.get_num_past_screens()):
            for index, row in enumerate(self.get_rows_for_past_screen(old_screen)):
                print(f"Screen {old_screen:02} Row {index:02}:{row}")

    def get_num_past_screens(self) -> int:
        return len(self.past_screens)

    def get_rows_for_past_screen(self, past_screen: int) -> List[str]:
        return self.get_rows(screen=self.past_screens[past_screen])

    def get_rows_with_attributes_for_past_screen(
        self, past_screen: int
    ) -> Tuple[List[str], List[str]]:
        return self.get_rows_with_attributes(screen=self.past_screens[past_screen])

    def get_rows_with_attributes_for_past_screens(
        self, past_screens: List[int]
    ) -> Tuple[List[str], List[str]]:
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

    def get_rows_with_attributes(
        self, screen: Optional[ScreenType] = None
    ) -> Tuple[List[str], List[str]]:
        if not screen:
            screen = self.output

        rows: List[str] = []
        attribute_rows: List[str] = []
        for y_pos in range(self.max_y):
            row = ""
            attribute_row = ""
            for x_pos in range(self.max_x):
                coord = (x_pos, y_pos)
                (char, attr) = screen[coord]
                row += char
                attribute_row += self.get_attribute_symbol_for_code(attr)
            rows.append(row)
            attribute_rows.append(attribute_row)
        return rows, attribute_rows

    def get_rows(self, screen: Optional[ScreenType] = None) -> List[str]:
        (rows, _) = self.get_rows_with_attributes(screen)
        return rows

    def get_attribute_symbol_for_code(self, code: int) -> str:
        symbol = ATTRIBUTE_SYMBOL_MAPPING.get(code, None)
        if symbol is None:
            raise ValueError(f"{code} not mapped")
        return symbol
