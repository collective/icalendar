"""Test vFrequency ical_value property."""

from icalendar.prop import vFrequency


def test_ical_value():
    """ical_value property returns the string value."""
    freq = vFrequency("DAILY")
    assert freq.ical_value == "DAILY"
    assert isinstance(freq.ical_value, str)
    
    freq2 = vFrequency("WEEKLY")
    assert freq2.ical_value == "WEEKLY"
