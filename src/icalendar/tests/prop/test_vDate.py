"""Test vDate ical_value property."""

from datetime import date

from icalendar.prop import vDate


def test_ical_value():
    """ical_value property returns the date value."""
    d = date(1997, 7, 14)
    vd = vDate(d)
    assert vd.ical_value == d
    assert isinstance(vd.ical_value, date)
