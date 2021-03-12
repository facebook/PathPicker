# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import signal
import sys
from types import FrameType
from typing import Dict, List, Tuple

from pathpicker import logger, output, usage_strings
from pathpicker.char_code_mapping import CODE_TO_CHAR
from pathpicker.color_printer import ColorPrinter
from pathpicker.curses_api import CursesApiBase
from pathpicker.key_bindings import KeyBindings
from pathpicker.line_format import LineBase, LineMatch
from pathpicker.screen import ScreenBase
from pathpicker.screen_flags import ScreenFlags


def signal_handler(_sig: int, _frame: FrameType) -> None:
    # from http://stackoverflow.com/a/1112350/948126
    # Lets just quit rather than signal.SIGINT printing the stack
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


CHROME_MIN_X = 5
CHROME_MIN_Y = 0

SELECT_MODE = "SELECT"
COMMAND_MODE = "COMMAND_MODE"
X_MODE = "X_MODE"

LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~!@#$%^&*()_+<>?{}|;'"

# options for displayed to the user at the bottom of the screen
SHORT_NAV_OPTION_SELECTION_STR = "[f|A] selection"
SHORT_NAV_OPTION_NAVIGATION_STR = "[down|j|up|k|space|b] navigation"
SHORT_NAV_OPTION_OPEN_STR = "[enter] open"
SHORT_NAV_OPTION_QUICK_SELECT_STR = "[x] quick select mode"
SHORT_NAV_OPTION_COMMAND_STR = "[c] command mode"

SHORT_COMMAND_USAGE = (
    "command examples: | git add | git checkout HEAD~1 -- | mv $F ../here/ |"
)
SHORT_COMMAND_PROMPT = "Type a command below! Paths will be appended or replace $F"
SHORT_COMMAND_PROMPT2 = "Enter a blank line to go back to the selection process"
SHORT_PATHS_HEADER = "Paths you have selected:"

INVISIBLE_CURSOR = 0
BLOCK_CURSOR = 2


class HelperChrome:
    def __init__(
        self, printer: ColorPrinter, screen_control: "Controller", flags: ScreenFlags
    ):
        self.printer = printer
        self.screen_control = screen_control
        self.flags = flags
        self.mode = SELECT_MODE
        self.width = 50
        self.sidebar_y = 0
        self.description_clear = True
        if self.get_is_sidebar_mode():
            logger.add_event("init_wide_mode")
        else:
            logger.add_event("init_narrow_mode")

    def output(self, mode: str) -> None:
        self.mode = mode
        for func in [self.output_side, self.output_bottom, self.toggle_cursor]:
            try:
                func()
            except curses.error:
                pass

    def output_description(self, line_obj: LineMatch) -> None:
        self.output_description_pane(line_obj)

    def toggle_cursor(self) -> None:
        # only include cursor when in command mode
        if self.mode == COMMAND_MODE:
            curses.curs_set(BLOCK_CURSOR)
        else:
            curses.curs_set(INVISIBLE_CURSOR)

    def reduce_max_y(self, max_y: int) -> int:
        if self.get_is_sidebar_mode():
            return max_y
        return max_y - 4

    def reduce_max_x(self, max_x: int) -> int:
        if not self.get_is_sidebar_mode():
            return max_x
        return max_x - self.width

    def get_min_x(self) -> int:
        if self.mode == COMMAND_MODE:
            return 0
        return self.screen_control.get_chrome_boundaries()[0]

    def get_min_y(self) -> int:
        return self.screen_control.get_chrome_boundaries()[1]

    def get_is_sidebar_mode(self) -> bool:
        _max_y, max_x = self.screen_control.get_screen_dimensions()
        return max_x > 200

    def trim_line(self, line: str, width: int) -> str:
        return line[:width]

    def output_description_pane(self, line_obj: LineMatch) -> None:
        if not self.get_is_sidebar_mode():
            return
        _max_y, max_x = self.screen_control.get_screen_dimensions()
        border_x = max_x - self.width
        start_y = self.sidebar_y + 1
        start_x = border_x + 2
        header_line = "Description for " + line_obj.path + " :"
        line_prefix = "    * "
        desc_lines = [
            line_obj.get_time_last_accessed(),
            line_obj.get_time_last_modified(),
            line_obj.get_owner_user(),
            line_obj.get_owner_group(),
            line_obj.get_file_size(),
            line_obj.get_length_in_lines(),
        ]
        self.printer.addstr(start_y, start_x, header_line)
        y_pos = start_y + 2
        for desc_line in desc_lines:
            desc_line = self.trim_line(desc_line, max_x - start_x - len(line_prefix))
            self.printer.addstr(y_pos, start_x, line_prefix + desc_line)
            y_pos = y_pos + 1
        self.description_clear = False

    # to fix bug where description pane may not clear on scroll
    def clear_description_pane(self) -> None:
        if self.description_clear:
            return
        max_y, max_x = self.screen_control.get_screen_dimensions()
        border_x = max_x - self.width
        start_y = self.sidebar_y + 1
        self.printer.clear_square(start_y, max_y - 1, border_x + 2, max_x)
        self.description_clear = True

    def output_side(self) -> None:
        if not self.get_is_sidebar_mode():
            return
        max_y, max_x = self.screen_control.get_screen_dimensions()
        border_x = max_x - self.width
        if self.mode == COMMAND_MODE:
            border_x = len(SHORT_COMMAND_PROMPT) + 20
        usage_lines = usage_strings.USAGE_PAGE.split("\n")
        if self.mode == COMMAND_MODE:
            usage_lines = usage_strings.USAGE_COMMAND.split("\n")
        for index, usage_line in enumerate(usage_lines):
            self.printer.addstr(self.get_min_y() + index, border_x + 2, usage_line)
            self.sidebar_y = self.get_min_y() + index
        for y_pos in range(self.get_min_y(), max_y):
            self.printer.addstr(y_pos, border_x, "|")

    def output_bottom(self) -> None:
        if self.get_is_sidebar_mode():
            return
        max_y, max_x = self.screen_control.get_screen_dimensions()
        border_y = max_y - 2
        # first output text since we might throw an exception during border
        usage_str = {
            SELECT_MODE: self.get_short_nav_usage_string(),
            X_MODE: self.get_short_nav_usage_string(),
            COMMAND_MODE: SHORT_COMMAND_USAGE,
        }[self.mode]
        border_str = "_" * (max_x - self.get_min_x() - 0)
        self.printer.addstr(border_y, self.get_min_x(), border_str)
        self.printer.addstr(border_y + 1, self.get_min_x(), usage_str)

    def get_short_nav_usage_string(self) -> str:
        nav_options = [
            SHORT_NAV_OPTION_SELECTION_STR,
            SHORT_NAV_OPTION_NAVIGATION_STR,
            SHORT_NAV_OPTION_OPEN_STR,
            SHORT_NAV_OPTION_QUICK_SELECT_STR,
            SHORT_NAV_OPTION_COMMAND_STR,
        ]

        # it does not make sense to give the user the option to "open" the selection
        # in all-input mode
        if self.flags.get_all_input():
            nav_options.remove(SHORT_NAV_OPTION_OPEN_STR)

        return ", ".join(nav_options)


class ScrollBar:
    def __init__(
        self,
        printer: ColorPrinter,
        lines: Dict[int, LineBase],
        screen_control: "Controller",
    ):
        self.printer = printer
        self.screen_control = screen_control
        self.num_lines = len(lines)
        self.box_start_fraction = 0.0
        self.box_stop_fraction = 0.0
        self.calc_box_fractions()

        # see if we are activated
        self.activated = True
        max_y, _max_x = self.screen_control.get_screen_dimensions()
        if self.num_lines < max_y:
            self.activated = False
            logger.add_event("no_scrollbar")
        else:
            logger.add_event("needed_scrollbar")

    def get_is_activated(self) -> bool:
        return self.activated

    def calc_box_fractions(self) -> None:
        # what we can see is basically the fraction of our screen over
        # total num lines
        max_y, _max_x = self.screen_control.get_screen_dimensions()
        frac_displayed = min(1.0, (max_y / float(self.num_lines)))
        self.box_start_fraction = -self.screen_control.get_scroll_offset() / float(
            self.num_lines
        )
        self.box_stop_fraction = self.box_start_fraction + frac_displayed

    def output(self) -> None:
        if not self.activated:
            return
        for func in [
            self.output_caps,
            self.output_base,
            self.output_box,
            self.output_border,
        ]:
            try:
                func()
            except curses.error:
                pass

    def get_min_y(self) -> int:
        return self.screen_control.get_chrome_boundaries()[1] + 1

    def get_x(self) -> int:
        return 0

    def output_border(self) -> None:
        x_pos = self.get_x() + 4
        max_y, _max_x = self.screen_control.get_screen_dimensions()
        for y_pos in range(0, max_y):
            self.printer.addstr(y_pos, x_pos, " ")

    def output_box(self) -> None:
        max_y, _max_x = self.screen_control.get_screen_dimensions()
        top_y = max_y - 2
        min_y = self.get_min_y()
        diff = top_y - min_y
        x_pos = self.get_x()

        box_start_y = int(diff * self.box_start_fraction) + min_y
        box_stop_y = int(diff * self.box_stop_fraction) + min_y

        self.printer.addstr(box_start_y, x_pos, "/-\\")
        for y_pos in range(box_start_y + 1, box_stop_y):
            self.printer.addstr(y_pos, x_pos, "|-|")
        self.printer.addstr(box_stop_y, x_pos, "\\-/")

    def output_caps(self) -> None:
        x_pos = self.get_x()
        max_y, _max_x = self.screen_control.get_screen_dimensions()
        for y_pos in [self.get_min_y() - 1, max_y - 1]:
            self.printer.addstr(y_pos, x_pos, "===")

    def output_base(self) -> None:
        x_pos = self.get_x()
        max_y, _max_x = self.screen_control.get_screen_dimensions()
        for y_pos in range(self.get_min_y(), max_y - 1):
            self.printer.addstr(y_pos, x_pos, " . ")


class Controller:
    def __init__(
        self,
        flags: ScreenFlags,
        key_bindings: KeyBindings,
        stdscr: ScreenBase,
        line_objs: Dict[int, LineBase],
        curses_api: CursesApiBase,
    ):
        self.stdscr = stdscr
        self.curses_api = curses_api
        self.curses_api.use_default_colors()
        self.color_printer = ColorPrinter(self.stdscr, curses_api)
        self.flags = flags
        self.key_bindings = key_bindings

        self.line_objs = line_objs
        self.hover_index = 0
        self.scroll_offset = 0
        self.scroll_bar = ScrollBar(self.color_printer, line_objs, self)
        self.helper_chrome = HelperChrome(self.color_printer, self, flags)
        self.old_max_y, self.old_max_x = self.get_screen_dimensions()
        self.mode = SELECT_MODE

        # lets loop through and split
        self.line_matches: List[LineMatch] = []

        for line_obj in self.line_objs.values():
            line_obj.set_controller(self)
            if isinstance(line_obj, LineMatch):
                self.line_matches.append(line_obj)

        # begin tracking dirty state
        self.dirty = False
        self.dirty_indexes: List[int] = []

        if self.flags.args.all:
            self.toggle_select_all()

        self.num_lines = len(line_objs.keys())
        self.num_matches = len(self.line_matches)

        self.set_hover(self.hover_index, True)

        # the scroll offset might not start off
        # at 0 if our first real match is WAY
        # down the screen -- so lets init it to
        # a valid value after we have all our line objects
        self.update_scroll_offset()

        logger.add_event("init")

    def get_scroll_offset(self) -> int:
        return self.scroll_offset

    def get_screen_dimensions(self) -> Tuple[int, int]:
        return self.stdscr.getmaxyx()

    def get_chrome_boundaries(self) -> Tuple[int, int, int, int]:
        max_y, max_x = self.stdscr.getmaxyx()
        min_x = (
            CHROME_MIN_X
            if self.scroll_bar.get_is_activated() or self.mode == X_MODE
            else 0
        )
        max_y = self.helper_chrome.reduce_max_y(max_y)
        max_x = self.helper_chrome.reduce_max_x(max_x)
        # format of (MINX, MINY, MAXX, MAXY)
        return min_x, CHROME_MIN_Y, max_x, max_y

    def get_viewport_height(self) -> int:
        (_min_x, min_y, _max_x, max_y) = self.get_chrome_boundaries()
        return max_y - min_y

    def set_hover(self, index: int, val: bool) -> None:
        self.line_matches[index].set_hover(val)

    def toggle_select(self) -> None:
        self.line_matches[self.hover_index].toggle_select()

    def toggle_select_all(self) -> None:
        paths = set()
        for line in self.line_matches:
            if line.get_path() not in paths:
                paths.add(line.get_path())
                line.toggle_select()

    def set_select(self, val: bool) -> None:
        self.line_matches[self.hover_index].set_select(val)

    def describe_file(self) -> None:
        self.helper_chrome.output_description(self.line_matches[self.hover_index])

    def control(self) -> None:
        execute_keys = self.flags.get_execute_keys()

        # we start out by printing everything we need to
        self.print_all()
        self.reset_dirty()
        self.move_cursor()
        while True:
            if len(execute_keys) > 0:
                in_key = execute_keys.pop(0)
            else:
                in_key = self.get_key()
            self.check_resize()
            self.process_input(in_key)
            self.process_dirty()
            self.reset_dirty()
            self.move_cursor()
            self.stdscr.refresh()

    def check_resize(self) -> None:
        max_y, max_x = self.get_screen_dimensions()
        if max_y is not self.old_max_y or max_x is not self.old_max_x:
            # we resized so print all!
            self.print_all()
            self.reset_dirty()
            self.update_scroll_offset()
            self.stdscr.refresh()
            logger.add_event("resize")
        self.old_max_y, self.old_max_x = self.get_screen_dimensions()

    def update_scroll_offset(self) -> None:
        """
        yay scrolling logic! we will start simple here
        and basically just center the viewport to current
        matched line
        """
        window_height = self.get_viewport_height()
        half_height = int(round(window_height / 2.0))

        # important, we need to get the real SCREEN position
        # of the hover index, not its index within our matches
        hovered = self.line_matches[self.hover_index]
        desired_top_row = hovered.get_screen_index() - half_height

        old_offset = self.scroll_offset
        desired_top_row = max(desired_top_row, 0)
        new_offset = -desired_top_row
        # lets add in some leeway -- don't bother repositioning
        # if the old offset is within 1/2 of the window height
        # of our desired (unless we absolutely have to)
        if (
            abs(new_offset - old_offset) > half_height / 2
            or self.hover_index + old_offset < 0
        ):
            # need to reassign now we have gone too far
            self.scroll_offset = new_offset
        if old_offset is not self.scroll_offset:
            self.dirty_all()

        # also update our scroll bar
        self.scroll_bar.calc_box_fractions()

    def page_down(self) -> None:
        page_height = int(self.get_viewport_height() * 0.5)
        self.move_index(page_height)

    def page_up(self) -> None:
        page_height = int(self.get_viewport_height() * 0.5)
        self.move_index(-page_height)

    def move_index(self, delta: int) -> None:
        new_index = (self.hover_index + delta) % self.num_matches
        self.jump_to_index(new_index)
        # also clear the description pane if necessary
        self.helper_chrome.clear_description_pane()

    def jump_to_index(self, new_index: int) -> None:
        self.set_hover(self.hover_index, False)
        self.hover_index = new_index
        self.set_hover(self.hover_index, True)
        self.update_scroll_offset()

    def process_input(self, key: str) -> None:
        if key in ["k", "UP"]:
            self.move_index(-1)
        elif key in ["j", "DOWN"]:
            self.move_index(1)
        elif key == "x":
            self.toggle_x_mode()
        elif key == "c":
            self.begin_enter_command()
        elif key in [" ", "NPAGE"]:
            self.page_down()
        elif key in ["b", "PPAGE"]:
            self.page_up()
        elif key in ["g", "HOME"]:
            self.jump_to_index(0)
        elif (key == "G" and not self.mode == X_MODE) or key == "END":
            self.jump_to_index(self.num_matches - 1)
        elif key == "d":
            self.describe_file()
        elif key == "f":
            self.toggle_select()
        elif key == "F":
            self.toggle_select()
            self.move_index(1)
        elif key == "A" and not self.mode == X_MODE:
            self.toggle_select_all()
        elif key == "ENTER" and (
            not self.flags.get_all_input() or self.flags.get_preset_command()
        ):
            # it does not make sense to process an 'ENTER' keypress if we're in
            # the allInput mode and there is not a preset command.
            self.on_enter()
        elif key == "q":
            output.output_nothing()
            # this will get the appropriate selection and save it to a file for
            # reuse before exiting the program
            self.get_paths_to_use()
            self.curses_api.exit()
        elif self.mode == X_MODE and key in LABELS:
            self.select_x_mode(key)

        for bound_key, command in self.key_bindings:
            if key == bound_key:
                self.execute_preconfigured_command(command)

    def get_paths_to_use(self) -> List[LineMatch]:
        # if we have selected paths, those, otherwise hovered
        to_use = self.get_selected_paths()
        if not to_use:
            to_use = self.get_hovered_paths()

        # save the selection we are using
        if self.curses_api.allow_file_output():
            output.output_selection(to_use)
        return to_use

    def get_selected_paths(self) -> List[LineMatch]:
        return [
            line_obj
            for index, line_obj in enumerate(self.line_matches)
            if line_obj.get_selected()
        ]

    def get_hovered_paths(self) -> List[LineMatch]:
        return [
            line_obj
            for index, line_obj in enumerate(self.line_matches)
            if index == self.hover_index
        ]

    def show_and_get_command(self) -> str:
        path_objs = self.get_paths_to_use()
        paths = [path_obj.get_path() for path_obj in path_objs]
        max_y, max_x = self.get_screen_dimensions()

        # Alright this is a bit tricky -- for tall screens, we try to aim
        # the command prompt right at the middle of the screen so you don't
        # have to shift your eyes down or up a bunch
        begin_height = int(round(max_y / 2) - len(paths) / 2.0)
        # but if you have a TON of paths, we are going to start printing
        # way off screen. in this case lets just slap the prompt
        # at the bottom so we can fit as much as possible.
        #
        # There could better option here to slowly increase the prompt
        # height to the bottom, but this is good enough for now...
        if begin_height <= 1:
            begin_height = max_y - 6

        border_line = "=" * len(SHORT_COMMAND_PROMPT)
        prompt_line = "." * len(SHORT_COMMAND_PROMPT)
        # from helper chrome code
        max_path_length = max_x - 5
        if self.helper_chrome.get_is_sidebar_mode():
            # need to be shorter to not go into side bar
            max_path_length = len(SHORT_COMMAND_PROMPT) + 18

        # first lets print all the paths
        start_height = begin_height - 1 - len(paths)
        try:
            self.color_printer.addstr(start_height - 3, 0, border_line)
            self.color_printer.addstr(start_height - 2, 0, SHORT_PATHS_HEADER)
            self.color_printer.addstr(start_height - 1, 0, border_line)
        except curses.error:
            pass

        for index, path in enumerate(paths):
            try:
                self.color_printer.addstr(
                    start_height + index, 0, path[0:max_path_length]
                )
            except curses.error:
                pass

        # first print prompt
        try:
            self.color_printer.addstr(begin_height, 0, SHORT_COMMAND_PROMPT)
            self.color_printer.addstr(begin_height + 1, 0, SHORT_COMMAND_PROMPT2)
        except curses.error:
            pass
        # then line to distinguish and prompt line
        try:
            self.color_printer.addstr(begin_height - 1, 0, border_line)
            self.color_printer.addstr(begin_height + 2, 0, border_line)
            self.color_printer.addstr(begin_height + 3, 0, prompt_line)
        except curses.error:
            pass

        self.stdscr.refresh()
        self.curses_api.echo()
        max_x = int(round(max_x - 1))

        return self.stdscr.getstr(begin_height + 3, 0, max_x)

    def begin_enter_command(self) -> None:
        self.stdscr.erase()
        # first check if they are trying to enter command mode
        # but already have a command...
        if self.flags.get_preset_command():
            self.helper_chrome.output(self.mode)
            (min_x, min_y, _, max_y) = self.get_chrome_boundaries()
            y_start = (max_y + min_y) // 2 - 3
            self.print_provided_command_warning(y_start, min_x)
            self.stdscr.refresh()
            self.get_key()
            self.mode = SELECT_MODE
            self.dirty_all()
            return

        self.mode = COMMAND_MODE
        self.helper_chrome.output(self.mode)
        logger.add_event("enter_command_mode")

        command = self.show_and_get_command()
        if len(command) == 0:
            # go back to selection mode and repaint
            self.mode = SELECT_MODE
            self.curses_api.noecho()
            self.dirty_all()
            logger.add_event("exit_command_mode")
            return
        line_objs = self.get_paths_to_use()
        output.exec_composed_command(command, line_objs)
        sys.exit(0)

    def execute_preconfigured_command(self, command: str) -> None:
        line_objs = self.get_paths_to_use()
        output.exec_composed_command(command, line_objs)
        sys.exit(0)

    def on_enter(self) -> None:
        line_objs = self.get_paths_to_use()
        if not line_objs:
            # nothing selected, assume we want hovered
            line_objs = self.get_hovered_paths()
        logger.add_event("selected_num_files", len(line_objs))

        # commands passed from the command line get used immediately
        preset_command = self.flags.get_preset_command()
        if len(preset_command) > 0:
            output.exec_composed_command(preset_command, line_objs)
        else:
            output.edit_files(line_objs)

        sys.exit(0)

    def reset_dirty(self) -> None:
        # reset all dirty state for our components
        self.dirty = False
        self.dirty_indexes = []

    def dirty_line(self, index: int) -> None:
        self.dirty_indexes.append(index)

    def dirty_all(self) -> None:
        self.dirty = True

    def process_dirty(self) -> None:
        if self.dirty:
            self.print_all()
            return
        (_min_x, min_y, _max_x, max_y) = self.get_chrome_boundaries()
        did_clear_line = False
        for index in self.dirty_indexes:
            y_pos = min_y + index + self.get_scroll_offset()
            if min_y <= y_pos < max_y:
                did_clear_line = True
                self.clear_line(y_pos)
                self.line_objs[index].output(self.color_printer)
        if did_clear_line and self.helper_chrome.get_is_sidebar_mode():
            # now we need to output the chrome again since on wide
            # monitors we will have cleared out a line of the chrome
            self.helper_chrome.output(self.mode)

    def clear_line(self, y_pos: int) -> None:
        """Clear a line of content, excluding the chrome"""
        (min_x, _, _, _) = self.get_chrome_boundaries()
        (_, max_x) = self.stdscr.getmaxyx()
        chars_to_delete = range(min_x, max_x)
        # we go in the **reverse** order since the original documentation
        # of delchar (http://dell9.ma.utexas.edu/cgi-bin/man-cgi?delch+3)
        # mentions that delchar actually moves all the characters to the right
        # of the cursor
        for x_pos in reversed(chars_to_delete):
            self.stdscr.delch(y_pos, x_pos)

    def print_all(self) -> None:
        self.stdscr.erase()
        self.print_lines()
        self.print_scroll()
        self.print_x_mode()
        self.print_chrome()

    def print_lines(self) -> None:
        for line_obj in self.line_objs.values():
            line_obj.output(self.color_printer)

    def print_scroll(self) -> None:
        self.scroll_bar.output()

    def print_provided_command_warning(self, y_start: int, x_start: int) -> None:
        self.color_printer.addstr(
            y_start,
            x_start,
            "Oh no! You already provided a command so you cannot enter command mode.",
            self.color_printer.get_attributes(curses.COLOR_WHITE, curses.COLOR_RED, 0),
        )

        self.color_printer.addstr(
            y_start + 1,
            x_start,
            f'The command you provided was "{self.flags.get_preset_command()}" ',
        )
        self.color_printer.addstr(
            y_start + 2, x_start, "Press any key to go back to selecting paths."
        )

    def print_chrome(self) -> None:
        self.helper_chrome.output(self.mode)

    def move_cursor(self) -> None:
        x_pos = CHROME_MIN_X if self.scroll_bar.get_is_activated() else 0
        y_pos = (
            self.line_matches[self.hover_index].get_screen_index() + self.scroll_offset
        )
        self.stdscr.move(y_pos, x_pos)

    def get_key(self) -> str:
        char_code = self.stdscr.getch()
        return CODE_TO_CHAR.get(char_code, "")

    def toggle_x_mode(self) -> None:
        self.mode = X_MODE if self.mode != X_MODE else SELECT_MODE
        self.print_all()

    def print_x_mode(self) -> None:
        if self.mode == X_MODE:
            (max_y, _) = self.scroll_bar.screen_control.get_screen_dimensions()
            top_y = max_y - 2
            min_y = self.scroll_bar.get_min_y() - 1
            for i in range(min_y, top_y + 1):
                idx = i - min_y
                if idx < len(LABELS):
                    self.color_printer.addstr(i, 1, LABELS[idx])

    def select_x_mode(self, key: str) -> None:
        if LABELS.index(key) >= len(self.line_objs):
            return
        line_obj = self.line_objs[LABELS.index(key) - self.scroll_offset]
        if isinstance(line_obj, LineMatch):
            line_match_index = self.line_matches.index(line_obj)
            self.hover_index = line_match_index
            self.toggle_select()
