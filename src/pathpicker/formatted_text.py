# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import re
from collections import namedtuple
from typing import Optional, Tuple

from pathpicker.color_printer import ColorPrinter


class FormattedText:

    """A piece of ANSI escape formatted text which responds
    to str() returning the plain text and knows how to print
    itself out using ncurses"""

    ANSI_ESCAPE_FORMATTING = r"\x1b\[([^mK]*)[mK]"
    BOLD_ATTRIBUTE = 1
    UNDERLINE_ATTRIBUTE = 4
    Range = namedtuple("Range", "bottom top")
    FOREGROUND_RANGE = Range(30, 39)
    BACKGROUND_RANGE = Range(40, 49)

    def __init__(self, text: Optional[str] = None):
        self.text = text

        if self.text is not None:
            self.segments = re.split(self.ANSI_ESCAPE_FORMATTING, self.text)
            # re.split will insert a empty string if there is a match at the beginning
            # or it will return [string] if there is no match
            # create the invariant that every segment has a formatting segment, e.g
            # we will always have FORMAT, TEXT, FORMAT, TEXT
            self.segments.insert(0, "")
            self.plain_text = "".join(self.segments[1::2])

    def __str__(self) -> str:
        return self.plain_text

    @classmethod
    def parse_formatting(cls, formatting: str) -> Tuple[int, int, int]:
        """Parse ANSI formatting; the formatting passed in should be
        stripped of the control characters and ending character"""
        fg_color = -1  # -1 default means "use default", not "use white/black"
        bg_color = -1
        other = 0
        int_values = [int(value) for value in formatting.split(";") if value]
        for code in int_values:
            if cls.FOREGROUND_RANGE.bottom <= code <= cls.FOREGROUND_RANGE.top:
                fg_color = code - cls.FOREGROUND_RANGE.bottom
            elif cls.BACKGROUND_RANGE.bottom <= code <= cls.BACKGROUND_RANGE.top:
                bg_color = code - cls.BACKGROUND_RANGE.bottom
            elif code == cls.BOLD_ATTRIBUTE:
                other = other | curses.A_BOLD
            elif code == cls.UNDERLINE_ATTRIBUTE:
                other = other | curses.A_UNDERLINE

        return fg_color, bg_color, other

    @classmethod
    def get_sequence_for_attributes(
        cls, fg_color: int, bg_color: int, attr: int
    ) -> str:
        """Return a fully formed escape sequence for the color pair
        and additional attributes"""
        return (
            "\x1b["
            + str(cls.FOREGROUND_RANGE.bottom + fg_color)
            + ";"
            + str(cls.BACKGROUND_RANGE.bottom + bg_color)
            + ";"
            + str(attr)
            + "m"
        )

    def print_text(
        self, y_pos: int, x_pos: int, printer: ColorPrinter, max_len: int
    ) -> None:
        """Print out using ncurses. Note that if any formatting changes
        occur, the attribute set is changed and not restored"""
        printed_so_far = 0
        for index, val in enumerate(self.segments):
            if printed_so_far >= max_len:
                break
            if index % 2 == 1:
                # text
                to_print = val[0 : max_len - printed_so_far]
                printer.addstr(
                    y_pos, x_pos + printed_so_far, to_print, ColorPrinter.CURRENT_COLORS
                )
                printed_so_far += len(to_print)
            else:
                # formatting
                printer.set_attributes(*self.parse_formatting(val))

    def find_segment_place(self, to_go: int) -> Tuple[int, int]:
        index = 1

        while index < len(self.segments):
            to_go -= len(self.segments[index])
            if to_go < 0:
                return index, to_go

            index += 2

        if to_go == 0:
            # we could reach here if the requested place is equal
            # to the very end of the string (as we do a <0 above).
            return index - 2, len(self.segments[index - 2])
        raise AssertionError("Unreachable")

    def breakat(self, where: int) -> Tuple["FormattedText", "FormattedText"]:
        """Break the formatted text at the point given and return
        a new tuple of two FormattedText representing the before and
        after"""
        # FORMAT, TEXT, FORMAT, TEXT, FORMAT, TEXT
        # --before----, segF,   seg,  ----after--
        #
        # to
        #
        # FORMAT, TEXT, FORMAT, TEXTBEFORE, FORMAT, TEXTAFTER, FORMAT, TEXT
        # --before----, segF,   [before],   segF,   [after],   -----after--
        # ----index---------------/
        (index, split_point) = self.find_segment_place(where)
        text_segment = self.segments[index]
        before_text = text_segment[:split_point]
        after_text = text_segment[split_point:]
        before_segments = self.segments[:index]
        after_segments = self.segments[index + 1 :]

        formatting_for_segment = self.segments[index - 1]

        before_formatted_text = FormattedText()
        after_formatted_text = FormattedText()
        before_formatted_text.segments = before_segments + [before_text]
        after_formatted_text.segments = (
            [formatting_for_segment] + [after_text] + after_segments
        )
        before_formatted_text.plain_text = self.plain_text[:where]
        after_formatted_text.plain_text = self.plain_text[where:]

        return before_formatted_text, after_formatted_text
