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
    "unsupported property",  # CIFuzz: dateutil tzical ValueError: unsupported property: RRULE
    # dateutil.tz.tzical ValueErrors on malformed VTIMEZONE after parse stays
    # open for #1712; not TEXT-filter bugs. The ignore list is how this
    # project's fuzzer treats expected third-party parse failures (same
    # pattern as "not enough values to unpack").
    "unsupported ",  # dateutil tzical: unsupported TZID/TZOFFSET/TZNAME parm
    "empty offset",
    "invalid offset",
    "empty property name",
    "mandatory TZID",
    "mandatory DTSTART",  # CIFuzz crash-ba601c46 on this PR
    "mandatory TZOFFSETFROM",
    "no timezones defined",
    "more than one timezone available",
    "Unsupported DTSTART param",
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
        # CIFuzz: Contentline AssertionError on raw LF in a non-TEXT RRULE key (#1445).
        if _CONTENTLINE_NEWLINE_ASSERT in str(e):
            return -1
        raise
