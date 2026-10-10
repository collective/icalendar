"""otc offset converison

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.14
"""

from datetime import timedelta
from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vUTCOffset
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal

mark_values = pytest.mark.parametrize(
    ("offset", "xcal"),
    [
        (timedelta(hours=2), "+02:00"),
        (timedelta(hours=-10, minutes=-30), "-10:30"),
        (timedelta(hours=3, minutes=0, seconds=10), "+03:00:10"),
    ],
)


@mark_values
def test_to_xcal(offset, xcal):
    """Convert to xcal."""
    e = to_xcal(vUTCOffset(offset))
    assert isinstance(e, ET.Element)
    assert e.tag == "utc-offset"
    assert e.text == xcal
    assert ET.tostring(e, encoding="unicode") == f"<utc-offset>{xcal}</utc-offset>"


@mark_values
def test_from_xcal_from_dt_class(offset, xcal):
    """Parse from xcal."""
    element = list2xml(["x-prop", ["utc-offset", xcal]])
    result = vUTCOffset.from_xcal(element)
    assert result.td == offset


@pytest.mark.parametrize(
    ("offset", "xcal"),
    [
        (timedelta(), "-00:00"),
        (timedelta(), "00:00"),
        (timedelta(), "+00:00"),
        (timedelta(hours=2), "02:00"),
        (timedelta(hours=3, minutes=0, seconds=10), "03:00:10"),
    ],
)
def test_parse_positive_values(offset, xcal):
    """Test the + at the start."""
    element = list2xml(["x-prop", ["utc-offset", xcal]])
    result = vUTCOffset.from_xcal(element)
    assert result.td == offset


@pytest.mark.parametrize(
    ("xcal"),
    ["INVALID", "P15DT5H", "", "1:1:1", "2025111", "2025-11-10T00:0010", "2025111A"],
)
def test_invalid_value_from_xcal(xcal):
    """Parse from xcal with invalid value."""
    element = list2xml(["x-prop", ["utc-offset", xcal]])
    with pytest.raises(XCalParsingError) as error:
        vUTCOffset.from_xcal(element)
    assert (
        error.value.message
        == f"Expected utc-offset format https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.14, got {xcal!r} in /x-prop/utc-offset[1]."
    )
