"""This is a collection of test files that are generated from the fuzzer.

The fuzzer finds the cases in which the icalendar module breaks.
These test cases reproduce the failure.
Some more tests can be added to make sure that the behavior works properly.
"""

def fuzz_calendar_v1(from_ical, calendar_string: str, multiple: bool, should_walk: bool):
    """Take a from_ical function and reproduce the error.

    The calendar_string is a fuzzed input.
    """
    cal = from_ical(calendar_string, multiple=multiple)

    if not multiple:
        cal = [cal]
    for c in cal:
        if should_walk:
            for event in cal.walk('VEVENT'):
                event.to_ical()
        else:
            cal.to_ical()
