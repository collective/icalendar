"""geo converison

https://datatracker.ietf.org/doc/html/rfc6321#section-3.4.1.2
https://datypic.com/sc/xsd/t-xsd_float.html
"""

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.geo import vGeo
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal_list


@pytest.fixture(params=[(37.386013, -122.082932), (-37.3860155, 12.082932)])
def lat_lon(request):
    """Variating the values."""
    return request.param


@pytest.fixture
def lat(lat_lon):
    return lat_lon[0]


@pytest.fixture
def lon(lat_lon):
    return lat_lon[1]


@pytest.fixture
def geo_list(lat, lon):
    return ["geo", ["latitude", str(lat)], ["longitude", str(lon)]]


@pytest.fixture
def geo_xml(geo_list):
    return list2xml(geo_list)


def test_parse_geo(geo_xml, lat, lon):
    """Test parsing a valid xml."""
    geo = vGeo.from_xcal(geo_xml)
    assert geo.latitude == lat
    assert geo.longitude == lon


def test_error_when_missing_latitude(geo_list):
    """Latitude is missing."""
    geo_list.pop(1)
    with pytest.raises(XCalParsingError) as e:
        vGeo.from_xcal(list2xml(geo_list))
    assert e.value.message == "Tag latitude not found in /geo."


def test_error_when_missing_longitude(geo_list):
    """Latitude is missing."""
    geo_list.pop(2)
    with pytest.raises(XCalParsingError) as e:
        vGeo.from_xcal(list2xml(geo_list))
    assert e.value.message == "Tag longitude not found in /geo."


def test_error_with_empty_geo():
    with pytest.raises(XCalParsingError) as e:
        vGeo.from_xcal(list2xml(["geo"]))
    assert e.value.message == "Tag latitude not found in /geo."


def test_to_xcal(lat, lon, geo_list):
    """Test  xCal conversion."""
    geo = vGeo((lat, lon))
    result = to_xcal_list(geo, wrap=False)
    assert result == geo_list
