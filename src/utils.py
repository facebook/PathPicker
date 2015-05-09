"""
Module where the utility functions, classes are.
"""
from contextlib import contextmanager
import curses


@contextmanager
def ignore_curse_errors():
    """
    Context manager to ignore the errors from `curses`

    Example::
        with ignore_curse_errors():
            func()
    """
    try:
        yield
    except curses.error:
        pass
