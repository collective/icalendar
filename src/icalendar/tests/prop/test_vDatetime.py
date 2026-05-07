"""Test vDatetime ical_value property."""

from datetime import datetime

from icalendar.prop import vDatetime


def test_ical_value():
    """ical_value property returns the datetime value."""
    dt = datetime(2021, 3, 2, 10, 15, 0)
    vdt = vDatetime(dt)
    assert vdt.ical_value == dt
    assert isinstance(vdt.ical_value, datetime)
