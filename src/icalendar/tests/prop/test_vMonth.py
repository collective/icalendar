"""Tests for vMonth.ical_value (issue #876)."""

import pytest

from icalendar.prop import vMonth, vRecur


@pytest.mark.parametrize("month", [1, 5, 12])
def test_ical_value_is_the_month_number(month):
    """ical_value returns the month number for a regular month."""
    assert vMonth(month).ical_value == month


def test_ical_value_is_a_plain_int():
    """ical_value is a plain int, not a vMonth (isinstance would accept both)."""
    assert type(vMonth(5).ical_value) is int


def test_ical_value_of_leap_month_is_the_month_number():
    """A RFC 7529 leap month like 5L returns its month number."""
    assert vMonth("5L").ical_value == 5


def test_leap_flag_is_unchanged():
    """The leap flag stays available on vMonth itself."""
    assert vMonth("5L").leap is True
    assert vMonth(5).leap is False


def test_ical_value_inside_a_recurrence_rule():
    """BYMONTH values parsed from an RRULE expose ical_value."""
    month = vRecur.from_ical("FREQ=YEARLY;BYMONTH=5")["BYMONTH"][0]
    assert month.ical_value == 5
