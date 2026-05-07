"""Test vRecur ical_value property."""

from icalendar.prop import vRecur


def test_ical_value():
    """ical_value property returns the dict value."""
    rrule = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    ical_val = rrule.ical_value
    
    assert isinstance(ical_val, dict)
    assert "FREQ" in ical_val
    assert "COUNT" in ical_val
    assert ical_val["FREQ"] == ["DAILY"]
    assert ical_val["COUNT"] == [10]


def test_ical_value_complex():
    """ical_value property returns complex recurrence rules."""
    rrule = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20231231T235959Z")
    ical_val = rrule.ical_value
    
    assert isinstance(ical_val, dict)
    assert "FREQ" in ical_val
    assert "BYDAY" in ical_val
    assert "UNTIL" in ical_val
