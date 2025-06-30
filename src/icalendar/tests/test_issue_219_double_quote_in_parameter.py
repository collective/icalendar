"""This tests handling of the double quote in the parameters.

See https://github.com/collective/icalendar/issues/219
"""


def test_parse_with_double_quotes(calendars):
    """When we parse the calendar with escaped double quotes, we still need to not error."""
