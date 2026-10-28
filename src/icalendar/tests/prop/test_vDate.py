"""Test vDate"""

from datetime import date

from icalendar.prop import vDate


def test_ical_value():
    """ical_value property returns a date value."""
    value = date(2005, 11, 14)
    ical_date = vDate(value).ical_value
    assert ical_date == value
    assert type(ical_date) is date
