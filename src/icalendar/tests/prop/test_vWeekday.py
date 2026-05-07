"""Test vWeekday ical_value property."""

from icalendar.prop import vWeekday


def test_ical_value():
    """ical_value property returns the string value."""
    # Simple weekday
    wd = vWeekday("MO")
    assert wd.ical_value == "MO"
    assert isinstance(wd.ical_value, str)
    
    # Weekday with relative position
    wd2 = vWeekday("2FR")
    assert wd2.ical_value == "2FR"
    assert isinstance(wd2.ical_value, str)
    
    # Negative relative position
    wd3 = vWeekday("-1SU")
    assert wd3.ical_value == "-1SU"
    assert isinstance(wd3.ical_value, str)
