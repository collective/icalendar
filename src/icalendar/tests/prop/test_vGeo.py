"""Test vGeo ical_value property."""

from icalendar.prop import vGeo


def test_ical_value():
    """ical_value property returns the (latitude, longitude) tuple."""
    geo = vGeo((37.386013, -122.082932))
    assert geo.ical_value == (37.386013, -122.082932)
    assert isinstance(geo.ical_value, tuple)
    assert len(geo.ical_value) == 2
