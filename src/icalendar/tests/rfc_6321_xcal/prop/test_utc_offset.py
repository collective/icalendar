"""utc-offset conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.14
"""

from datetime import timedelta
from xml.etree import ElementTree as ET

import pytest

from icalendar import vUTCOffset
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory

from .common import XML_WHITESPACE

mark_values = pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("-05:00", vUTCOffset(timedelta(hours=-5))),
        ("+01:00", vUTCOffset(timedelta(hours=1))),
        ("+00:00", vUTCOffset(timedelta(0))),
        ("-05:30:20", vUTCOffset(-timedelta(hours=5, minutes=30, seconds=20))),
    ],
)


@mark_values
def test_to_xcal(value, expected):
    """Convert to xcal."""
    e = expected.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "utc-offset"
    assert e.text == value
    assert ET.tostring(e, encoding="unicode") == f"<utc-offset>{value}</utc-offset>"


@mark_values
def test_from_xcal(types_factory: TypesFactory, value, expected):
    """Parse from xcal."""
    e = ET.Element("utc-offset")
    e.text = value
    result = types_factory.from_xcal("tzoffsetto", e)
    assert isinstance(result, vUTCOffset)
    assert result == expected


def test_whitespace_is_collapsed(types_factory: TypesFactory):
    """White Space: collapse"""
    e = ET.Element("utc-offset")
    e.text = XML_WHITESPACE + "-05:00" + XML_WHITESPACE
    assert types_factory.from_xcal("tzoffsetto", e) == vUTCOffset(timedelta(hours=-5))


@pytest.mark.parametrize(
    "invalid", [None, "", "-0500", "05:00:00:00", "INVALID", "-5:00"]
)
def test_invalid_value_from_xcal(types_factory: TypesFactory, invalid):
    """Parse from xcal with an invalid value."""
    e = ET.Element("utc-offset")
    e.text = invalid
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("tzoffsetto", e)
    assert error.value.parser == vUTCOffset
