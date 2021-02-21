# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import os
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from pathpicker import parse
from pathpicker.color_printer import ColorPrinter
from pathpicker.formatted_text import FormattedText
from pathpicker.parse import MatchResult

if TYPE_CHECKING:
    from pathpicker.screen_control import Controller


class LineBase(ABC):
    def __init__(self) -> None:
        self.controller: Optional["Controller"] = None

    def set_controller(self, controller: "Controller") -> None:
        self.controller = controller

    @abstractmethod
    def output(self, printer: ColorPrinter) -> None:
        pass


class SimpleLine(LineBase):
    def __init__(self, formatted_line: FormattedText, index: int):
        super().__init__()
        self.formatted_line = formatted_line
        self.index = index

    def output(self, printer: ColorPrinter) -> None:
        assert self.controller is not None
        (min_x, min_y, max_x, max_y) = self.controller.get_chrome_boundaries()
        max_len = min(max_x - min_x, len(str(self)))
        y_pos = min_y + self.index + self.controller.get_scroll_offset()

        if y_pos < min_y or y_pos >= max_y:
            # wont be displayed!
            return

        self.formatted_line.print_text(y_pos, min_x, printer, max_len)

    def __str__(self) -> str:
        return str(self.formatted_line)


class LineMatch(LineBase):
    ARROW_DECORATOR = "|===>"
    # this is inserted between long files, so it looks like
    # ./src/foo/bar/something|...|baz/foo.py
    TRUNCATE_DECORATOR = "|...|"

    def __init__(
        self,
        formatted_line: FormattedText,
        result: MatchResult,
        index: int,
        validate_file_exists: bool = False,
        all_input: bool = False,
    ):
        super().__init__()

        self.formatted_line = formatted_line
        self.index = index
        self.all_input = all_input

        path, num, matches = result

        self.path = (
            path
            if all_input
            else parse.prepend_dir(path, with_file_inspection=validate_file_exists)
        )
        self.num = num

        line = str(self.formatted_line)
        # save a bunch of stuff so we can
        # pickle
        self.start = matches.start()
        self.end = min(matches.end(), len(line))
        self.group: str = matches.group()

        # this is a bit weird but we need to strip
        # off the whitespace for the matches we got,
        # since matches like README are aggressive
        # about including whitespace. For most lines
        # this will be a no-op, but for lines like
        # "README        " we will reset end to
        # earlier
        string_subset = line[self.start : self.end]
        stripped_subset = string_subset.strip()
        trailing_whitespace = len(string_subset) - len(stripped_subset)
        self.end -= trailing_whitespace
        self.group = self.group[0 : len(self.group) - trailing_whitespace]

        self.selected = False
        self.hovered = False
        self.is_truncated = False

        # precalculate the pre, post, and match strings
        (self.before_text, _) = self.formatted_line.breakat(self.start)
        (_, self.after_text) = self.formatted_line.breakat(self.end)

        self.decorated_match = FormattedText()
        self.update_decorated_match()

    def toggle_select(self) -> None:
        self.set_select(not self.selected)

    def set_select(self, val: bool) -> None:
        self.selected = val
        self.update_decorated_match()

    def set_hover(self, val: bool) -> None:
        self.hovered = val
        self.update_decorated_match()

    def get_screen_index(self) -> int:
        return self.index

    def get_path(self) -> str:
        return self.path

    def get_file_size(self) -> str:
        size = os.path.getsize(self.path)
        for unit in ["B", "K", "M", "G", "T", "P", "E", "Z"]:
            if size < 1024:
                return f"size: {size}{unit}"
            size //= 1024
        raise AssertionError("Unreachable")

    def get_length_in_lines(self) -> str:
        output = subprocess.check_output(["wc", "-l", self.path])
        lines_count = output.strip().split()[0].decode("utf-8")
        lines_caption = "lines" if int(lines_count) > 1 else "line"
        return f"length: {lines_count} {lines_caption}"

    def get_time_last_accessed(self) -> str:
        time_accessed = time.strftime(
            "%m/%d/%Y %H:%M:%S", time.localtime(os.stat(self.path).st_atime)
        )
        return f"last accessed: {time_accessed}"

    def get_time_last_modified(self) -> str:
        time_modified = time.strftime(
            "%m/%d/%Y %H:%M:%S", time.localtime(os.stat(self.path).st_mtime)
        )
        return f"last modified: {time_modified}"

    def get_owner_user(self) -> str:
        user_owner_name = Path(self.path).owner()
        user_owner_id = os.stat(self.path).st_uid
        return f"owned by user: {user_owner_name}, {user_owner_id}"

    def get_owner_group(self) -> str:
        group_owner_name = Path(self.path).group()
        group_owner_id = os.stat(self.path).st_gid
        return f"owned by group: {group_owner_name}, {group_owner_id}"

    def get_dir(self) -> str:
        return os.path.dirname(self.path)

    def is_resolvable(self) -> bool:
        return not self.is_git_abbreviated_path()

    def is_git_abbreviated_path(self) -> bool:
        # this method mainly serves as a warning for when we get
        # git-abbrievated paths like ".../" that confuse users.
        parts = self.path.split(os.path.sep)
        return len(parts) > 0 and parts[0] == "..."

    def get_line_num(self) -> int:
        return self.num

    def get_selected(self) -> bool:
        return self.selected

    def get_before(self) -> str:
        return str(self.before_text)

    def get_after(self) -> str:
        return str(self.after_text)

    def get_match(self) -> str:
        return self.group

    def __str__(self) -> str:
        return (
            self.get_before()
            + "||"
            + self.get_match()
            + "||"
            + self.get_after()
            + "||"
            + str(self.num)
        )

    def update_decorated_match(self, max_len: Optional[int] = None) -> None:
        """Update the cached decorated match formatted string, and
        dirty the line, if needed"""
        if self.hovered and self.selected:
            attributes = (
                curses.COLOR_WHITE,
                curses.COLOR_RED,
                FormattedText.BOLD_ATTRIBUTE,
            )
        elif self.hovered:
            attributes = (
                curses.COLOR_WHITE,
                curses.COLOR_BLUE,
                FormattedText.BOLD_ATTRIBUTE,
            )
        elif self.selected:
            attributes = (
                curses.COLOR_WHITE,
                curses.COLOR_GREEN,
                FormattedText.BOLD_ATTRIBUTE,
            )
        elif not self.all_input:
            attributes = (0, 0, FormattedText.UNDERLINE_ATTRIBUTE)
        else:
            attributes = (0, 0, 0)

        decorator_text = self.get_decorator()

        # we may not be connected to a controller (during process_input,
        # for example)
        if self.controller:
            self.controller.dirty_line(self.index)

        plain_text = decorator_text + self.get_match()
        if max_len and len(plain_text + str(self.before_text)) > max_len:
            # alright, we need to chop the ends off of our
            # decorated match and glue them together with our
            # truncation decorator. We subtract the length of the
            # before text since we consider that important too.
            space_allowed = (
                max_len
                - len(self.TRUNCATE_DECORATOR)
                - len(decorator_text)
                - len(str(self.before_text))
            )
            mid_point = int(space_allowed / 2)
            begin_match = plain_text[0:mid_point]
            end_match = plain_text[-mid_point : len(plain_text)]
            plain_text = begin_match + self.TRUNCATE_DECORATOR + end_match

        self.decorated_match = FormattedText(
            FormattedText.get_sequence_for_attributes(*attributes) + plain_text
        )

    def get_decorator(self) -> str:
        if self.selected:
            return self.ARROW_DECORATOR
        return ""

    def print_up_to(
        self,
        text: FormattedText,
        printer: ColorPrinter,
        y_pos: int,
        x_pos: int,
        max_len: int,
    ) -> Tuple[int, int]:
        """Attempt to print maxLen characters, returning a tuple
        (x, maxLen) updated with the actual number of characters
        printed"""
        if max_len <= 0:
            return x_pos, max_len

        max_printable = min(len(str(text)), max_len)
        text.print_text(y_pos, x_pos, printer, max_printable)
        return x_pos + max_printable, max_len - max_printable

    def output(self, printer: ColorPrinter) -> None:
        assert self.controller is not None
        (min_x, min_y, max_x, max_y) = self.controller.get_chrome_boundaries()
        y_pos = min_y + self.index + self.controller.get_scroll_offset()

        if y_pos < min_y or y_pos >= max_y:
            # wont be displayed!
            return

        # we dont care about the after text, but we should be able to see
        # all of the decorated match (which means we need to see up to
        # the end of the decoratedMatch, aka include beforeText)
        important_text_length = len(str(self.before_text)) + len(
            str(self.decorated_match)
        )
        space_for_printing = max_x - min_x
        if important_text_length > space_for_printing:
            # hrm, we need to update our decorated match to show
            # a truncated version since right now we will print off
            # the screen. lets also dump the beforeText for more
            # space
            self.update_decorated_match(max_len=space_for_printing)
            self.is_truncated = True
        else:
            # first check what our expanded size would be:
            expanded_size = len(str(self.before_text)) + len(self.get_match())
            if expanded_size < space_for_printing and self.is_truncated:
                # if the screen gets resized, we might be truncated
                # from a previous render but **now** we have room.
                # in that case lets expand back out
                self.update_decorated_match()
                self.is_truncated = False

        max_len = max_x - min_x
        so_far = (min_x, max_len)

        so_far = self.print_up_to(self.before_text, printer, y_pos, *so_far)
        so_far = self.print_up_to(self.decorated_match, printer, y_pos, *so_far)
        so_far = self.print_up_to(self.after_text, printer, y_pos, *so_far)
