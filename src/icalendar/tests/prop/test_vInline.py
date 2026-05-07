"""Test vInline ical_value property."""

from icalendar.prop import vInline


def test_ical_value():
    """ical_value property returns the string value."""
    inline = vInline("some raw text")
    assert inline.ical_value == "some raw text"
    assert isinstance(inline.ical_value, str)
    
    inline2 = vInline("another value")
    assert inline2.ical_value == "another value"
