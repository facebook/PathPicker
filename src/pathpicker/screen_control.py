# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import curses
import signal
import sys

from pathpicker import logger, output, usage_strings
from pathpicker.char_code_mapping import CODE_TO_CHAR
from pathpicker.color_printer import ColorPrinter
from pathpicker.line_format import LineMatch


def signal_handler(_sig, _frame) -> None:
    # from http://stackoverflow.com/a/1112350/948126
    # Lets just quit rather than signal.SIGINT printing the stack
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


CHROME_MIN_X = 5
CHROME_MIN_Y = 0

SELECT_MODE = "SELECT"
COMMAND_MODE = "COMMAND_MODE"
X_MODE = "X_MODE"

lbls = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~!@#$%^&*()_+<>?{}|;'"

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
    def __init__(self, printer, screen_control, flags):
        self.printer = printer
        self.screen_control = screen_control
        self.flags = flags
        self.mode = SELECT_MODE
        self.WIDTH = 50
        self.SIDEBAR_Y = 0
        self.DESCRIPTION_CLEAR = True
        if self.get_is_sidebar_mode():
            logger.add_event("init_wide_mode")
        else:
            logger.add_event("init_narrow_mode")

    def output(self, mode):
        self.mode = mode
        for func in [self.output_side, self.output_bottom, self.toggle_cursor]:
            try:
                func()
            except curses.error:
                pass

    def output_description(self, line_obj):
        self.output_description_pane(line_obj)

    def toggle_cursor(self):
        # only include cursor when in command mode
        if self.mode == COMMAND_MODE:
            curses.curs_set(BLOCK_CURSOR)
        else:
            curses.curs_set(INVISIBLE_CURSOR)

    def reduce_max_y(self, max_y):
        if self.get_is_sidebar_mode():
            return max_y
        return max_y - 4

    def reduce_max_x(self, max_x):
        if not self.get_is_sidebar_mode():
            return max_x
        return max_x - self.WIDTH

    def get_min_x(self):
        if self.mode == COMMAND_MODE:
            return 0
        return self.screen_control.get_chrome_boundaries()[0]

    def get_min_y(self):
        return self.screen_control.get_chrome_boundaries()[1]

    def get_is_sidebar_mode(self):
        (_max_y, max_x) = self.screen_control.get_screen_dimensions()
        return max_x > 200

    def trim_line(self, line, width):
        return line[:width]

    def output_description_pane(self, line_obj):
        if not self.get_is_sidebar_mode():
            return
        (_max_y, max_x) = self.screen_control.get_screen_dimensions()
        border_x = max_x - self.WIDTH
        start_y = self.SIDEBAR_Y + 1
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
        y = start_y + 2
        for desc_line in desc_lines:
            desc_line = self.trim_line(desc_line, max_x - start_x - len(line_prefix))
            self.printer.addstr(y, start_x, line_prefix + desc_line)
            y = y + 1
        self.DESCRIPTION_CLEAR = False

    # to fix bug where description pane may not clear on scroll
    def clear_description_pane(self):
        if self.DESCRIPTION_CLEAR:
            return
        (max_y, max_x) = self.screen_control.get_screen_dimensions()
        border_x = max_x - self.WIDTH
        start_y = self.SIDEBAR_Y + 1
        self.printer.clear_square(start_y, max_y - 1, border_x + 2, max_x)
        self.DESCRIPTION_CLEAR = True

    def output_side(self):
        if not self.get_is_sidebar_mode():
            return
        (max_y, max_x) = self.screen_control.get_screen_dimensions()
        border_x = max_x - self.WIDTH
        if self.mode == COMMAND_MODE:
            border_x = len(SHORT_COMMAND_PROMPT) + 20
        usage_lines = usage_strings.USAGE_PAGE.split("\n")
        if self.mode == COMMAND_MODE:
            usage_lines = usage_strings.USAGE_COMMAND.split("\n")
        for index, usage_line in enumerate(usage_lines):
            self.printer.addstr(self.get_min_y() + index, border_x + 2, usage_line)
            self.SIDEBAR_Y = self.get_min_y() + index
        for y in range(self.get_min_y(), max_y):
            self.printer.addstr(y, border_x, "|")

    def output_bottom(self):
        if self.get_is_sidebar_mode():
            return
        (max_y, max_x) = self.screen_control.get_screen_dimensions()
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

    def get_short_nav_usage_string(self):
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
    def __init__(self, printer, lines, screen_control):
        self.printer = printer
        self.screen_control = screen_control
        self.num_lines = len(lines)
        self.box_start_fraction = 0.0
        self.box_stop_fraction = 0.0
        self.calc_box_fractions()

        # see if we are activated
        self.activated = True
        (max_y, _max_x) = self.screen_control.get_screen_dimensions()
        if self.num_lines < max_y:
            self.activated = False
            logger.add_event("no_scrollbar")
        else:
            logger.add_event("needed_scrollbar")

    def get_is_activated(self):
        return self.activated

    def calc_box_fractions(self):
        # what we can see is basically the fraction of our screen over
        # total num lines
        (max_y, _max_x) = self.screen_control.get_screen_dimensions()
        frac_displayed = min(1.0, (max_y / float(self.num_lines)))
        self.box_start_fraction = -self.screen_control.get_scroll_offset() / float(
            self.num_lines
        )
        self.box_stop_fraction = self.box_start_fraction + frac_displayed

    def output(self):
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

    def get_min_y(self):
        return self.screen_control.get_chrome_boundaries()[1] + 1

    def get_x(self):
        return 0

    def output_border(self):
        x_pos = self.get_x() + 4
        (max_y, _max_x) = self.screen_control.get_screen_dimensions()
        for y_pos in range(0, max_y):
            self.printer.addstr(y_pos, x_pos, " ")

    def output_box(self):
        (max_y, _max_x) = self.screen_control.get_screen_dimensions()
        top_y = max_y - 2
        min_y = self.get_min_y()
        diff = top_y - min_y
        x = self.get_x()

        box_start_y = int(diff * self.box_start_fraction) + min_y
        box_stop_y = int(diff * self.box_stop_fraction) + min_y

        self.printer.addstr(box_start_y, x, "/-\\")
        for y_pos in range(box_start_y + 1, box_stop_y):
            self.printer.addstr(y_pos, x, "|-|")
        self.printer.addstr(box_stop_y, x, "\\-/")

    def output_caps(self):
        x_pos = self.get_x()
        (max_y, _max_x) = self.screen_control.get_screen_dimensions()
        for y_pos in [self.get_min_y() - 1, max_y - 1]:
            self.printer.addstr(y_pos, x_pos, "===")

    def output_base(self):
        x = self.get_x()
        (max_y, _max_x) = self.screen_control.get_screen_dimensions()
        for y_pos in range(self.get_min_y(), max_y - 1):
            self.printer.addstr(y_pos, x, " . ")


class Controller:
    def __init__(self, flags, key_bindings, stdscr, line_objs, curses_api):
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
        (self.old_max_y, self.old_max_x) = self.get_screen_dimensions()
        self.mode = SELECT_MODE

        # lets loop through and split
        self.line_matches = []

        for line_obj in self.line_objs.values():
            line_obj.controller = self
            if not line_obj.is_simple():
                self.line_matches.append(line_obj)

        # begin tracking dirty state
        self.dirty = False
        self.dirty_indexes = []

        if self.flags.args.all:
            self.toggle_select_all()

        self.num_lines = len(line_objs.keys())
        self.num_matches = len(self.line_matches)

        self.set_hover(self.hover_index, True)

        # the scroll offset might not start off
        # at 0 if our first real match is WAY
        # down the screen -- so lets init it to
        # a valid value after we have all our line objects
        self.updateScrollOffset()

        logger.add_event("init")

    def get_scroll_offset(self):
        return self.scroll_offset

    def get_screen_dimensions(self):
        return self.stdscr.getmaxyx()

    def get_chrome_boundaries(self):
        (max_y, max_x) = self.stdscr.getmaxyx()
        min_x = (
            CHROME_MIN_X
            if self.scroll_bar.get_is_activated() or self.mode == X_MODE
            else 0
        )
        max_y = self.helper_chrome.reduce_max_y(max_y)
        max_x = self.helper_chrome.reduce_max_x(max_x)
        # format of (MINX, MINY, MAXX, MAXY)
        return (min_x, CHROME_MIN_Y, max_x, max_y)

    def get_viewport_height(self):
        (_min_x, min_y, _max_x, max_y) = self.get_chrome_boundaries()
        return max_y - min_y

    def set_hover(self, index, val):
        self.line_matches[index].set_hover(val)

    def toggle_select(self):
        self.line_matches[self.hover_index].toggle_select()

    def toggle_select_all(self):
        paths = set()
        for line in self.line_matches:
            if line.get_path() not in paths:
                paths.add(line.get_path())
                line.toggle_select()

    def set_select(self, val):
        self.line_matches[self.hover_index].set_select(val)

    def describe_file(self):
        self.helper_chrome.output_description(self.line_matches[self.hover_index])

    def control(self):
        execute_keys = self.flags.get_execute_keys()

        # we start out by printing everything we need to
        self.printAll()
        self.resetDirty()
        self.moveCursor()
        while True:
            if len(execute_keys) > 0:
                inKey = execute_keys.pop(0)
            else:
                inKey = self.getKey()
            self.checkResize()
            self.processInput(inKey)
            self.processDirty()
            self.resetDirty()
            self.moveCursor()
            self.stdscr.refresh()

    def checkResize(self):
        (maxy, maxx) = self.get_screen_dimensions()
        if maxy is not self.old_max_y or maxx is not self.old_max_x:
            # we resized so print all!
            self.printAll()
            self.resetDirty()
            self.updateScrollOffset()
            self.stdscr.refresh()
            logger.add_event("resize")
        (self.old_max_y, self.old_max_x) = self.get_screen_dimensions()

    def updateScrollOffset(self):
        """
        yay scrolling logic! we will start simple here
        and basically just center the viewport to current
        matched line
        """
        windowHeight = self.get_viewport_height()
        halfHeight = int(round(windowHeight / 2.0))

        # important, we need to get the real SCREEN position
        # of the hover index, not its index within our matches
        hovered = self.line_matches[self.hover_index]
        desiredTopRow = hovered.get_screen_index() - halfHeight

        oldOffset = self.scroll_offset
        desiredTopRow = max(desiredTopRow, 0)
        newOffset = -desiredTopRow
        # lets add in some leeway -- dont bother repositioning
        # if the old offset is within 1/2 of the window height
        # of our desired (unless we absolutely have to)
        if (
            abs(newOffset - oldOffset) > halfHeight / 2
            or self.hover_index + oldOffset < 0
        ):
            # need to reassign now we have gone too far
            self.scroll_offset = newOffset
        if oldOffset is not self.scroll_offset:
            self.dirtyAll()

        # also update our scroll bar
        self.scroll_bar.calc_box_fractions()

    def pageDown(self):
        pageHeight = (int)(self.get_viewport_height() * 0.5)
        self.moveIndex(pageHeight)

    def pageUp(self):
        pageHeight = (int)(self.get_viewport_height() * 0.5)
        self.moveIndex(-pageHeight)

    def moveIndex(self, delta):
        newIndex = (self.hover_index + delta) % self.num_matches
        self.jumpToIndex(newIndex)
        # also clear the description pane if necessary
        self.helper_chrome.clear_description_pane()

    def jumpToIndex(self, newIndex):
        self.set_hover(self.hover_index, False)
        self.hover_index = newIndex
        self.set_hover(self.hover_index, True)
        self.updateScrollOffset()

    def processInput(self, key):
        if key in ["k", "UP"]:
            self.moveIndex(-1)
        elif key in ["j", "DOWN"]:
            self.moveIndex(1)
        elif key == "x":
            self.toggleXMode()
        elif key == "c":
            self.beginEnterCommand()
        elif key in [" ", "NPAGE"]:
            self.pageDown()
        elif key in ["b", "PPAGE"]:
            self.pageUp()
        elif key in ["g", "HOME"]:
            self.jumpToIndex(0)
        elif (key == "G" and not self.mode == X_MODE) or key == "END":
            self.jumpToIndex(self.num_matches - 1)
        elif key == "d":
            self.describe_file()
        elif key == "f":
            self.toggle_select()
        elif key == "F":
            self.toggle_select()
            self.moveIndex(1)
        elif key == "A" and not self.mode == X_MODE:
            self.toggle_select_all()
        elif key == "ENTER" and (
            not self.flags.get_all_input() or self.flags.get_preset_command()
        ):
            # it does not make sense to process an 'ENTER' keypress if we're in
            # the allInput mode and there is not a preset command.
            self.onEnter()
        elif key == "q":
            output.output_nothing()
            # this will get the appropriate selection and save it to a file for
            # reuse before exiting the program
            self.getPathsToUse()
            self.curses_api.exit()
        elif self.mode == X_MODE and key in lbls:
            self.selectXMode(key)

        for boundKey, command in self.key_bindings:
            if key == boundKey:
                self.executePreconfiguredCommand(command)

    def getPathsToUse(self):
        # if we have selected paths, those, otherwise hovered
        toUse = self.getSelectedPaths()
        if not toUse:
            toUse = self.getHoveredPaths()

        # save the selection we are using
        if self.curses_api.allow_file_output():
            output.output_selection(toUse)
        return toUse

    def getSelectedPaths(self):
        return [
            lineObj
            for (index, lineObj) in enumerate(self.line_matches)
            if lineObj.get_selected()
        ]

    def getHoveredPaths(self):
        return [
            lineObj
            for (index, lineObj) in enumerate(self.line_matches)
            if index == self.hover_index
        ]

    def showAndGetCommand(self):
        pathObjs = self.getPathsToUse()
        paths = [pathObj.get_path() for pathObj in pathObjs]
        (maxy, maxx) = self.get_screen_dimensions()

        # Alright this is a bit tricky -- for tall screens, we try to aim
        # the command prompt right at the middle of the screen so you dont
        # have to shift your eyes down or up a bunch
        beginHeight = int(round(maxy / 2) - len(paths) / 2.0)
        # but if you have a TON of paths, we are going to start printing
        # way off screen. in this case lets just slap the prompt
        # at the bottom so we can fit as much as possible.
        #
        # There could better option here to slowly increase the prompt
        # height to the bottom, but this is good enough for now...
        if beginHeight <= 1:
            beginHeight = maxy - 6

        borderLine = "=" * len(SHORT_COMMAND_PROMPT)
        promptLine = "." * len(SHORT_COMMAND_PROMPT)
        # from helper chrome code
        maxPathLength = maxx - 5
        if self.helper_chrome.get_is_sidebar_mode():
            # need to be shorter to not go into side bar
            maxPathLength = len(SHORT_COMMAND_PROMPT) + 18

        # first lets print all the paths
        startHeight = beginHeight - 1 - len(paths)
        try:
            self.color_printer.addstr(startHeight - 3, 0, borderLine)
            self.color_printer.addstr(startHeight - 2, 0, SHORT_PATHS_HEADER)
            self.color_printer.addstr(startHeight - 1, 0, borderLine)
        except curses.error:
            pass

        for index, path in enumerate(paths):
            try:
                self.color_printer.addstr(startHeight + index, 0, path[0:maxPathLength])
            except curses.error:
                pass

        # first print prompt
        try:
            self.color_printer.addstr(beginHeight, 0, SHORT_COMMAND_PROMPT)
            self.color_printer.addstr(beginHeight + 1, 0, SHORT_COMMAND_PROMPT2)
        except curses.error:
            pass
        # then line to distinguish and prompt line
        try:
            self.color_printer.addstr(beginHeight - 1, 0, borderLine)
            self.color_printer.addstr(beginHeight + 2, 0, borderLine)
            self.color_printer.addstr(beginHeight + 3, 0, promptLine)
        except curses.error:
            pass

        self.stdscr.refresh()
        self.curses_api.echo()
        maxX = int(round(maxx - 1))

        command = self.stdscr.getstr(beginHeight + 3, 0, maxX)
        return command

    def beginEnterCommand(self):
        self.stdscr.erase()
        # first check if they are trying to enter command mode
        # but already have a command...
        if self.flags.get_preset_command():
            self.helper_chrome.output(self.mode)
            (minX, minY, _, maxY) = self.get_chrome_boundaries()
            yStart = (maxY + minY) / 2 - 3
            self.printProvidedCommandWarning(yStart, minX)
            self.stdscr.refresh()
            self.getKey()
            self.mode = SELECT_MODE
            self.dirtyAll()
            return

        self.mode = COMMAND_MODE
        self.helper_chrome.output(self.mode)
        logger.add_event("enter_command_mode")

        command = self.showAndGetCommand()
        if len(command) == 0:
            # go back to selection mode and repaint
            self.mode = SELECT_MODE
            self.curses_api.noecho()
            self.dirtyAll()
            logger.add_event("exit_command_mode")
            return
        lineObjs = self.getPathsToUse()
        output.exec_composed_command(command, lineObjs)
        sys.exit(0)

    def executePreconfiguredCommand(self, command):
        lineObjs = self.getPathsToUse()
        output.exec_composed_command(command, lineObjs)
        sys.exit(0)

    def onEnter(self):
        lineObjs = self.getPathsToUse()
        if not lineObjs:
            # nothing selected, assume we want hovered
            lineObjs = self.getHoveredPaths()
        logger.add_event("selected_num_files", len(lineObjs))

        # commands passed from the command line get used immediately
        presetCommand = self.flags.get_preset_command()
        if len(presetCommand) > 0:
            output.exec_composed_command(presetCommand, lineObjs)
        else:
            output.edit_files(lineObjs)

        sys.exit(0)

    def resetDirty(self):
        # reset all dirty state for our components
        self.dirty = False
        self.dirty_indexes = []

    def dirtyLine(self, index):
        self.dirty_indexes.append(index)

    def dirtyAll(self):
        self.dirty = True

    def processDirty(self):
        if self.dirty:
            self.printAll()
            return
        (_minx, miny, _maxx, maxy) = self.get_chrome_boundaries()
        didClearLine = False
        for index in self.dirty_indexes:
            y = miny + index + self.get_scroll_offset()
            if miny <= y < maxy:
                didClearLine = True
                self.clearLine(y)
                self.line_objs[index].output(self.color_printer)
        if didClearLine and self.helper_chrome.get_is_sidebar_mode():
            # now we need to output the chrome again since on wide
            # monitors we will have cleared out a line of the chrome
            self.helper_chrome.output(self.mode)

    def clearLine(self, y):
        """Clear a line of content, excluding the chrome"""
        (minx, _, _, _) = self.get_chrome_boundaries()
        (_, maxx) = self.stdscr.getmaxyx()
        charsToDelete = range(minx, maxx)
        # we go in the **reverse** order since the original documentation
        # of delchar (http://dell9.ma.utexas.edu/cgi-bin/man-cgi?delch+3)
        # mentions that delchar actually moves all the characters to the right
        # of the cursor
        for x in reversed(charsToDelete):
            self.stdscr.delch(y, x)

    def printAll(self):
        self.stdscr.erase()
        self.printLines()
        self.printScroll()
        self.printXMode()
        self.printChrome()

    def printLines(self):
        for lineObj in self.line_objs.values():
            lineObj.output(self.color_printer)

    def printScroll(self):
        self.scroll_bar.output()

    def printProvidedCommandWarning(self, yStart, xStart):
        self.color_printer.addstr(
            yStart,
            xStart,
            "Oh no! You already provided a command so "
            + "you cannot enter command mode.",
            self.color_printer.get_attributes(curses.COLOR_WHITE, curses.COLOR_RED, 0),
        )

        self.color_printer.addstr(
            yStart + 1,
            xStart,
            'The command you provided was "%s" ' % self.flags.get_preset_command(),
        )
        self.color_printer.addstr(
            yStart + 2, xStart, "Press any key to go back to selecting paths."
        )

    def printChrome(self):
        self.helper_chrome.output(self.mode)

    def moveCursor(self):
        x = CHROME_MIN_X if self.scroll_bar.get_is_activated() else 0
        y = self.line_matches[self.hover_index].get_screen_index() + self.scroll_offset
        self.stdscr.move(y, x)

    def getKey(self):
        charCode = self.stdscr.getch()
        return CODE_TO_CHAR.get(charCode, "")

    def toggleXMode(self):
        self.mode = X_MODE if self.mode != X_MODE else SELECT_MODE
        self.printAll()

    def printXMode(self):
        if self.mode == X_MODE:
            (maxy, _) = self.scroll_bar.screen_control.get_screen_dimensions()
            topY = maxy - 2
            minY = self.scroll_bar.get_min_y() - 1
            for i in range(minY, topY + 1):
                idx = i - minY
                if idx < len(lbls):
                    self.color_printer.addstr(i, 1, lbls[idx])

    def selectXMode(self, key):
        if lbls.index(key) >= len(self.line_objs):
            return
        lineObj = self.line_objs[lbls.index(key) - self.scroll_offset]
        if isinstance(lineObj, LineMatch):
            lineMatchIndex = self.line_matches.index(lineObj)
            self.hover_index = lineMatchIndex
            self.toggle_select()
