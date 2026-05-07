"""Test vDuration ical_value property."""

from datetime import timedelta

from icalendar.prop import vDuration


def test_ical_value():
    """ical_value property returns the timedelta value."""
    td = timedelta(days=15, hours=5, seconds=20)
    vdur = vDuration(td)
    assert vdur.ical_value == td
    assert isinstance(vdur.ical_value, timedelta)
