"""Small, bounded iteration contracts used by Chapter 26.

Importing this module only defines constants and functions.  It does not read
input, print, open files, create processes, or start any iteration.
"""

from itertools import count, islice


MAX_SQUARES = 10_000


def strict_pairs(left, right):
    """Return pairs, rejecting unequal input lengths."""
    return list(zip(left, right, strict=True))


def _require_bounded_integer(value, *, name, maximum):
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if not 0 <= value <= maximum:
        raise ValueError(f"{name} must be between 0 and {maximum}")


def countdown(start):
    """Yield ``start`` down to 1 after validating a finite bound."""
    _require_bounded_integer(start, name="start", maximum=MAX_SQUARES)
    current = start
    while current > 0:
        yield current
        current -= 1


def bounded_squares(limit):
    """Yield the first ``limit`` squares from an otherwise infinite source."""
    _require_bounded_integer(limit, name="limit", maximum=MAX_SQUARES)
    squares = (number * number for number in count())
    yield from islice(squares, limit)


def flatten(groups):
    """Yield every value from each finite group in order."""
    for group in groups:
        yield from group


def reciprocals(values):
    """Yield reciprocals; an invalid later value fails when it is consumed."""
    for value in values:
        yield 1 / value


def managed_values(values, close):
    """Yield values and call ``close`` once when an active generator ends."""
    if not callable(close):
        raise TypeError("close must be callable")
    try:
        yield from values
    finally:
        close()
