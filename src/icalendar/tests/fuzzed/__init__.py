"""This is a collection of test files that are generated from the fuzzer.

The fuzzer finds the cases in which the icalendar module breaks.
These test cases reproduce the failure.
Some more tests can be added to make sure that the behavior works properly.
"""

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
    # TEXT parse no longer raises, so tzical can run on the same corpus item.
    "unsupported property",  # dateutil.tz.tzical: RRULE at VTIMEZONE level
]

_CONTENTLINE_NEWLINE_ASSERT = (
    "Content line can not contain unescaped new line characters."
)


def fuzz_v1_calendar(
    from_ical, calendar_string: str, multiple: bool, should_walk: bool
):
    """Take a from_ical function and reproduce the error.

    The calendar_string is a fuzzed input.
    """
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
    except (ValueError, TypeError) as e:
        if any(m in str(e) for m in _value_error_matches):
            return -1
        raise
    except AssertionError as e:
        # Same corpus path as above: a non-TEXT RRULE key can still carry a
        # raw LF. Contentline.__new__ must fail loudly (issue #1445); that is
        # not a TEXT sanitization miss. Other asserts still propagate.
        if _CONTENTLINE_NEWLINE_ASSERT in str(e):
            return -1
        raise
