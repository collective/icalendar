"""Test vGeo ical_value property."""

from icalendar.prop import vGeo


def test_ical_value_basic():
    """ical_value property returns tuple of (latitude, longitude)."""
    geo = vGeo((37.386013, -122.082932))
    assert geo.ical_value == (37.386013, -122.082932)
    assert isinstance(geo.ical_value, tuple)
    assert len(geo.ical_value) == 2


def test_ical_value_components():
    """ical_value property components match latitude and longitude."""
    lat, lon = 48.8566, 2.3522  # Paris
    geo = vGeo((lat, lon))
    assert geo.ical_value[0] == lat
    assert geo.ical_value[1] == lon
    assert geo.ical_value == (geo.latitude, geo.longitude)


def test_ical_value_from_ical():
    """ical_value property works with geo parsed from ical string."""
    coords = vGeo.from_ical("51.5074;-0.1278")  # London
    geo = vGeo(coords)
    assert geo.ical_value == (51.5074, -0.1278)
    assert geo.ical_value[0] == 51.5074  # latitude
    assert geo.ical_value[1] == -0.1278  # longitude


def test_ical_value_negative_coordinates():
    """ical_value property handles negative coordinates."""
    geo = vGeo((-33.8688, 151.2093))  # Sydney
    assert geo.ical_value == (-33.8688, 151.2093)
    assert geo.ical_value[0] < 0  # Southern hemisphere
    assert geo.ical_value[1] > 0  # Eastern hemisphere
