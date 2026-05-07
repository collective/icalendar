"""Test vMonth ical_value property."""

from icalendar.prop import vMonth


def test_ical_value():
    """ical_value property returns the int value."""
    month = vMonth(1)
    assert month.ical_value == 1
    assert isinstance(month.ical_value, int)
    
    # Test with leap month
    leap_month = vMonth("5L")
    assert leap_month.ical_value == 5
    assert isinstance(leap_month.ical_value, int)
