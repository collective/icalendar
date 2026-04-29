"""Tests for Issue https://github.com/collective/icalendar/issues/1237"""

from datetime import datetime

from icalendar import Calendar, vPeriod


def test_reproduce_example(calendars):
    """Reproduce the example from the issue."""
    calendar: Calendar = calendars.issue_1237_x_property
    period = calendar["x-filter-date-range"]
    assert isinstance(period, vPeriod)
    assert period.start == datetime(2025, 2, 2)
    assert period.end == datetime(2025, 2, 3)
