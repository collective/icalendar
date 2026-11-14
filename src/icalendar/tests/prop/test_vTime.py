"""Test vTime property."""

from datetime import time, timezone

from icalendar.prop import vTime


def test_ical_value():
    """ical_value returns the time value."""
    value = time(8, 30, 0)
    ical_time = vTime(value).ical_value
    assert ical_time == value
    assert type(ical_time) is time


def test_ical_value_utc():
    """ical_value keeps the UTC timezone."""
    value = time(13, 30, 0, tzinfo=timezone.utc)
    assert vTime(value).ical_value == value
