"""This is a collection of test files that are generated from the fuzzer.

The fuzzer finds the cases in which the icalendar module breaks.
These test cases reproduce the failure.
Some more tests can be added to make sure that the behavior works properly.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from icalendar.compatibility import Self


class Predicate:
    """Check if an exception is expected during fuzzing.

    Predicates can be combined with ``&``, ``|`` and ``~``.

    Parameters:
        func: Returns ``True`` if the exception is expected.
    """

    def __init__(self, func: Callable[[BaseException], bool]) -> None:
        self.func: Callable[[BaseException], bool] = func

    def __call__(self, exception: BaseException) -> bool:
        return self.func(exception)

    def __and__(self, other: Callable[[BaseException], bool]) -> Self:
        return self.__class__(lambda ex: self(ex) and other(ex))

    def __or__(self, other: Callable[[BaseException], bool]) -> Self:
        return self.__class__(lambda ex: self(ex) or other(ex))

    def __invert__(self) -> Self:
        return self.__class__(lambda ex: not self(ex))


_value_error_matches = [
    "component",
    "parse",
    "Expected",
    "Wrong date format",
    "END encountered",
    "vDDD",
    "recurrence",
    "Offset must",
    "Invalid iCalendar",
    "alue MUST",
    "Key name",
    "Invalid content line",
    "Content line could not be parsed",
    "does not exist",
    "base 64",
    "must use datetime",
    "Unknown date type",
    "Wrong",
    "Start time",
    "iCalendar",
    "recurrence",
    "float, float",
    "utc offset",
    "parent",
    "MUST be a datetime",
    "Invalid month:",
    "must have exactly",  # vCard field count validation (ADR, N)
    "must have at least",  # vCard ORG minimum field validation
    "not enough values to unpack",  # dateutil rejects a malformed VTIMEZONE content line
    "Content line can not contain unescaped new line characters.",  # Contentline after #1559
]

# The current check: a ValueError or TypeError with one of the substrings above.
# See https://github.com/collective/icalendar/issues/1759
_value_error_message = Predicate(
    lambda e: (
        isinstance(e, (ValueError, TypeError))
        and any(m in str(e) for m in _value_error_matches)
    )
)

# An exception is ignored during fuzzing if any of these predicates matches.
_expected_exceptions: list[Predicate] = [
    _value_error_message,
]


def is_expected_exception(exception: BaseException) -> bool:
    """Check if the fuzzer can ignore this exception.

    Parameters:
        exception: The exception raised for a fuzzed input.

    Returns:
        ``True`` if any predicate in the list of expected exceptions matches.
    """
    return any(predicate(exception) for predicate in _expected_exceptions)


def format_fuzz_log(
    from_ical, multiple: bool, should_walk: bool, calendar_string: str | bytes
) -> str:
    """Format the log entry for fuzzed test case extraction.

    Outputs entrypoint name, parameter values, and base64-encoded calendar content.
    """
    import base64

    try:
        # print the ICS file for the test case extraction
        # see https://stackoverflow.com/a/27367173/1320237
        encoded = base64.b64encode(
            calendar_string.encode("UTF-8", "surrogateescape")
            if isinstance(calendar_string, str)
            else calendar_string
        ).decode("ASCII")
    except UnicodeEncodeError as e:
        encoded = str(e)
    return (
        f"{_get_name_of_caller()} {from_ical.__qualname__} multiple={multiple} "
        f"should_walk={should_walk} {encoded}"
    )


def _get_name_of_caller(skip: int = 0) -> str:
    stack = inspect.stack()
    relevant_index = skip + 2  # ignore own and caller frame
    if relevant_index < len(stack) and (frame := stack[relevant_index]):
        return frame.function
    return "<unknown source>"


def fuzz_v1_calendar(
    from_ical, calendar_string: str, multiple: bool, should_walk: bool
):
    """Take a from_ical function and reproduce the error.

    The calendar_string is a fuzzed input.
    """
    print(format_fuzz_log(from_ical, multiple, should_walk, calendar_string))
    try:
        cal = from_ical(calendar_string, multiple=multiple)

        if not multiple:
            cal = [cal]
        for c in cal:
            if should_walk:
                for event in c.walk("VEVENT"):
                    event.to_ical()
            else:
                c.to_ical()
    except Exception as e:
        if is_expected_exception(e):
            return -1
        raise
