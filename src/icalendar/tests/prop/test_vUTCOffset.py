"""Test vUTCOffset ical_value property."""

from datetime import timedelta

from icalendar.prop import vUTCOffset


def test_ical_value():
    """ical_value property returns the timedelta value."""
    td = timedelta(hours=-5)
    offset = vUTCOffset(td)
    assert offset.ical_value == td
    assert isinstance(offset.ical_value, timedelta)
