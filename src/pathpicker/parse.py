# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import re
import subprocess
from functools import partial
from typing import Callable, List, Match, NamedTuple, NewType, Optional, Pattern, Tuple

from pathpicker import logger
from pathpicker.repos import REPOS

MatchResult = NewType("MatchResult", Tuple[str, int, Match])

MASTER_REGEX = re.compile(
    r"(/?([a-z.A-Z0-9\-_]+/)+[@a-zA-Z0-9\-_+.]+\.[a-zA-Z0-9]{1,10})[:-]?(\d+)?"
)
MASTER_REGEX_MORE_EXTENSIONS = re.compile(
    r"(/?([a-z.A-Z0-9\-_]+/)+[@a-zA-Z0-9\-_+.]+\.[a-zA-Z0-9-~]{1,30})[:-]?(\d+)?"
)
HOMEDIR_REGEX = re.compile(
    r"(~/([a-z.A-Z0-9\-_]+/)+[@a-zA-Z0-9\-_+.]+\.[a-zA-Z0-9]{1,10})[:-]?(\d+)?"
)
OTHER_BGS_RESULT_REGEX = re.compile(
    r"(/?([a-z.A-Z0-9\-_]+/)+[a-zA-Z0-9_.]{3,})[:-]?(\d+)"
)
ENTIRE_TRIMMED_LINE_IF_NOT_WHITESPACE = re.compile(r"(\S.*\S|\S)")
JUST_FILE_WITH_NUMBER = re.compile(
    r"([@%+a-z.A-Z0-9\-_]+\.[a-zA-Z]{1,10})[:-](\d+)(\s|$|:)+"
)
JUST_FILE = re.compile(r"([@%+a-z.A-Z0-9\-_]+\.[a-zA-Z]{1,10})(\s|$|:)+")
JUST_EMACS_TEMP_FILE = re.compile(r"([@%+a-z.A-Z0-9\-_]+\.[a-zA-Z]{1,10}~)(\s|$|:)+")
JUST_VIM_TEMP_FILE = re.compile(r"(#[@%+a-z.A-Z0-9\-_]+\.[a-zA-Z]{1,10}#)(\s|$|:)+")
# start with a normal char for ls -l
JUST_FILE_WITH_SPACES = re.compile(
    r"([a-zA-Z][@+a-z. A-Z0-9\-_]+\.[a-zA-Z]{1,10})(\s|$|:)+"
)
FILE_NO_PERIODS = re.compile(
    (
        r"("
        # Recognized files starting with a dot followed by at least 3 characters
        r"((/?([a-z.A-Z0-9\-_]+/))?\.[a-zA-Z0-9\-_]{3,}[a-zA-Z0-9\-_/]*)"
        # or
        r"|"
        # Recognize files containing at least one slash
        r"([a-z.A-Z0-9\-_/]+/[a-zA-Z0-9\-_]+)"
        # or
        r"|"
        # Recognize files starting with capital letter and ending in "file".
        # eg. Makefile
        r"([A-Z][a-zA-Z]{2,}file)"
        # end trying to capture
        r")"
        # Regardless of the above case, here's how the file name should terminate
        r"(\s|$|:)+"
    )
)

MASTER_REGEX_WITH_SPACES_AND_WEIRD_FILES = re.compile(
    (
        # begin the capture
        r"("
        # capture some pre-dir stuff like / and ./
        r"(?:"
        r"\.?/"
        r")?"  # thats optional
        # now we look at directories. The 'character class ' allowed before the '/'
        # is either a real character or a character and a space. This allows
        # multiple spaces in a directory as long as each space is followed by
        # a normal character, but it does not allow multiple continguous spaces
        # which would otherwise gobble up too much whitespace.
        #
        # Thus, these directories will match:
        #   /something foo/
        #   / a b c d e/
        #   /normal/
        #
        # but these will not:
        #   /two  spaces  here/
        #   /ending in a space /
        r"(([a-z.A-Z0-9\-_]|\s[a-zA-Z0-9\-_])+/)+"
        # Recognized files starting with a dot followed by at least 3 characters
        r"((/?([a-z.A-Z0-9\-_]+/))?\.[a-zA-Z0-9\-_]{3,}[a-zA-Z0-9\-_/]*)"
        # or
        r"|"
        # Recognize files containing at least one slash
        r"([a-z.A-Z0-9\-_/]+/[a-zA-Z0-9\-_]+)"
        # or
        r"|"
        # Recognize files starting with capital letter and ending in "file".
        # eg. Makefile
        r"([A-Z][a-zA-Z]{2,}file)"
        r")"
    )
)

MASTER_REGEX_WITH_SPACES = re.compile(
    (
        # begin the capture
        r"("
        # capture some pre-dir stuff like / and ./
        r"(?:"
        r"\.?/"
        r")?"  # thats optional
        # now we look at directories. The 'character class ' allowed before the '/'
        # is either a real character or a character and a space. This allows
        # multiple spaces in a directory as long as each space is followed by
        # a normal character, but it does not allow multiple continguous spaces
        # which would otherwise gobble up too much whitespace.
        #
        # Thus, these directories will match:
        #   /something foo/
        #   / a b c d e/
        #   /normal/
        #
        # but these will not:
        #   /two  spaces  here/
        #   /ending in a space /
        r"(([a-z.A-Z0-9\-_]|\s[a-zA-Z0-9\-_])+/)+"
        # we do similar for the filename part. the 'character class' is
        # char or char with space following, with some added tokens like @
        # for retina files.
        r"([(),%@a-zA-Z0-9\-_+.]|\s[,()@%a-zA-Z0-9\-_+.])+"
        # extensions dont allow spaces
        r"\.[a-zA-Z0-9-]{1,30}"
        # end capture
        ")"
        # optionally capture the line number
        r"[:-]?(\d+)?"
    )
)


class RegexConfig(NamedTuple):
    name: str
    regex: Pattern
    preferred_regex: Optional[Pattern] = None
    num_index: int = 2
    no_num: bool = False
    only_with_file_inspection: bool = False
    with_all_lines_matched: bool = False


REGEX_WATERFALL: List[RegexConfig] = [
    # Homedirs need a separate regex.
    RegexConfig("HOMEDIR_REGEX", HOMEDIR_REGEX),
    # The master regex matches tbgs results with
    # line numbers, so we prefer that and test it first.
    RegexConfig(
        "MASTER_REGEX",
        MASTER_REGEX,
        # one real quick check -- did we find a better match
        # earlier in the regex?
        preferred_regex=OTHER_BGS_RESULT_REGEX,
    ),
    # If something clearly looks like an *bgs result but
    # just has a weird filename (like all caps with no extension)
    # then we can match that as well. Note that we require
    # the line number match since otherwise this would be too lax
    # of a regex.
    RegexConfig("OTHER_BGS_RESULT_REGEX", OTHER_BGS_RESULT_REGEX),
    RegexConfig(
        "MASTER_REGEX_MORE_EXTENSIONS",
        MASTER_REGEX_MORE_EXTENSIONS,
        only_with_file_inspection=True,
    ),
    # We would overmatch on wayyyyy too many things if we
    # allowed spaces everywhere, but with filesystem validation
    # and the final fallback we can include them.
    RegexConfig(
        "MASTER_REGEX_WITH_SPACES",
        MASTER_REGEX_WITH_SPACES,
        num_index=4,
        only_with_file_inspection=True,
    ),
    RegexConfig(
        "MASTER_REGEX_WITH_SPACES_AND_WEIRD_FILES",
        MASTER_REGEX_WITH_SPACES_AND_WEIRD_FILES,
        num_index=4,
        only_with_file_inspection=True,
    ),
    # An Emacs and Vim backup/temporary/save file of the form: #example.txt#
    RegexConfig(
        "JUST_VIM_TEMP_FILE",
        JUST_VIM_TEMP_FILE,
        no_num=True,
    ),
    # An Emacs backup/temporary/save file with a tilde at the end: example.txt~
    RegexConfig(
        "JUST_EMACS_TEMP_FILE",
        JUST_EMACS_TEMP_FILE,
        no_num=True,
    ),
    # File (without directory) and a number. Ex:
    # $ grep -n my_pattern A.txt B.txt
    # A.txt:100 my_pattern
    RegexConfig(
        "JUST_FILE_WITH_NUMBER",
        JUST_FILE_WITH_NUMBER,
        num_index=1,
    ),
    # Ok maybe its just a normal file (with a dot)
    # so lets test for that if the above fails
    RegexConfig(
        "JUST_FILE",
        JUST_FILE,
        no_num=True,
    ),
    # Ok if that's not there, try do to filesystem validation
    # for just files with spaces
    RegexConfig(
        "JUST_FILE_WITH_SPACES",
        JUST_FILE_WITH_SPACES,
        no_num=True,
        only_with_file_inspection=True,
    ),
    # Ok finally it might be a file with no periods. we test
    # this last since its more restrictive, because we don't
    # want to match things like cx('foo/root'). hence
    # we require some minimum number of slashes and minimum
    # file name length
    RegexConfig(
        "FILE_NO_PERIODS",
        FILE_NO_PERIODS,
        no_num=True,
    ),
    RegexConfig(
        "ENTIRE_TRIMMED_LINE_IF_NOT_WHITESPACE",
        ENTIRE_TRIMMED_LINE_IF_NOT_WHITESPACE,
        no_num=True,
        with_all_lines_matched=True,
    ),
]


# Attempts to resolve the root directory of the
# repository in which path resides (i.e. the current directory).
# both git and hg have commands for this, so let's just use those.
def get_repo_path() -> str:
    proc = subprocess.Popen(
        ["git rev-parse --show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    stdout, stderr = proc.communicate()

    # If there was no error return the output
    if not stderr:
        logger.add_event("using_git")
        return stdout

    proc = subprocess.Popen(
        ["hg root"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    stdout, stderr = proc.communicate()

    # If there was no error return the output
    if not stderr:
        logger.add_event("using_hg")
        return stdout

    # Not a git or hg repo, go with current dir as a default
    logger.add_event("used_outside_repo")
    return "./"


PREPEND_PATH = f"{get_repo_path().strip()}/"


# returns a filename and (optional) line number
# if it matches
def match_line(
    line: str, validate_file_exists: bool = False, all_input: bool = False
) -> Optional[MatchResult]:
    if not validate_file_exists:
        results = match_line_impl(line, with_all_lines_matched=all_input)
        return results[0] if results else None
    results = match_line_impl(
        line, with_file_inspection=True, with_all_lines_matched=all_input
    )
    if not results:
        return None
    # ok now we are going to check if this result is an actual
    # file...
    for result in results:
        (file_path, _, _) = result
        if (
            os.path.isfile(prepend_dir(file_path, with_file_inspection=True))
            or file_path[0:4] == ".../"
        ):
            return result
    return None


def match_line_impl(
    line: str, with_file_inspection: bool = False, with_all_lines_matched: bool = False
) -> List[MatchResult]:
    # ok new behavior -- we will actually collect **ALL** results
    # of the regexes since filesystem validation might filter some
    # of the earlier ones out (particularly those with hyphens)
    results = []
    for regex_config in REGEX_WATERFALL:
        regex = regex_config.regex
        if regex_config.with_all_lines_matched != with_all_lines_matched:
            continue
        if regex_config.only_with_file_inspection and not with_file_inspection:
            continue

        matches = regex.search(line)
        if not matches:
            continue

        # mypy needs some help here to resolve types correctly
        unpack_matches_num_index_var: Callable = partial(
            unpack_matches, num_index=regex_config.num_index
        )
        unpack_matches_no_num_var: Callable = unpack_matches_no_num
        unpack_func: Callable = (
            unpack_matches_no_num_var
            if regex_config.no_num
            else unpack_matches_num_index_var
        )

        if not regex_config.preferred_regex:
            results.append(unpack_func(matches))
            continue

        # check the preferred_regex
        preferred_regex = regex_config.preferred_regex
        other_matches = preferred_regex.search(line)
        if not other_matches:
            results.append(unpack_func(matches))
            continue
        if other_matches.start() < matches.start():
            # we found a better result earlier, so return that
            results.append(unpack_func(other_matches))
            continue
        results.append(unpack_func(matches))
    # nothing matched at all
    return results


def prepend_dir(file: str, with_file_inspection: bool = False) -> str:
    if not file or len(file) < 2:
        return file

    if file[0] == "/":
        return file

    if file[0:4] == ".../":
        # these are the gross git abbreviated paths, so
        # return early since we cant do anything here
        return file

    if file[0:2] == "~/":
        # need to absolute it
        return os.path.expanduser(file)

    # if it starts with relative dirs (grep), then that's the easiest
    # because abspath will resolve this
    if file[0:2] == "./" or file[0:3] == "../":
        return file

    # some peeps do forcedir and expand the path beforehand,
    # so lets check for that case here
    first = file.split(os.sep)[0]
    if first == "home" and not os.environ.get("FPP_DISABLE_PREPENDING_HOME_WITH_SLASH"):
        # already absolute, easy
        return "/" + file

    if first in REPOS + (os.environ.get("FPP_REPOS") or "").split(","):
        return os.path.expanduser("~/" + file)

    if "/" not in file:
        # assume current dir like ./
        return "./" + file

    # git show and diff has a/stuff and b/stuff, so handle that. git
    # status never does this so we don't need to worry about relative dirs
    if file[0:2] == "a/" or file[0:2] == "b/":
        return PREPEND_PATH + file[2:]

    split_up = file.split("/")
    if split_up[0] == "www":
        return PREPEND_PATH + "/".join(split_up[1:])

    if not with_file_inspection:
        # hope
        return PREPEND_PATH + "/".join(split_up)
    # Alright we need to handle the case where git status returns
    # relative paths where every other git command returns paths relative
    # to the top-level dir. so lets see if PREPEND_PATH is not a file whereas
    # relative is...
    top_level_path = PREPEND_PATH + "/".join(split_up)
    relative_path = "./" + "/".join(split_up)
    if not os.path.isfile(top_level_path) and os.path.isfile(relative_path):
        return relative_path
    return top_level_path


def unpack_matches_no_num(matches: Match) -> MatchResult:
    return MatchResult((matches.groups()[0], 0, matches))


def unpack_matches(matches: Match, num_index: int) -> MatchResult:
    groups = matches.groups()
    file = groups[0]
    num = 0 if groups[num_index] is None else int(groups[num_index])
    return MatchResult((file, num, matches))
