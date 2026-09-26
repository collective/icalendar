"""time conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.12
"""

from datetime import time, timezone
from xml.etree import ElementTree as ET

import pytest

from icalendar import vTime
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory

mark_values = pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12:30:00", vTime(time(12, 30))),
        ("00:00:00", vTime(time(0, 0))),
        ("23:59:59", vTime(time(23, 59, 59))),
        ("07:05:03Z", vTime(time(7, 5, 3, tzinfo=timezone.utc))),
    ],
)


@mark_values
def test_to_xcal(value, expected):
    """Convert to xcal."""
    e = expected.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "time"
    assert e.text == value
    assert ET.tostring(e, encoding="unicode") == f"<time>{value}</time>"


@mark_values
def test_from_xcal(x_sometime, types_factory: TypesFactory, value, expected):
    """Parse from xcal."""
    e = ET.Element("time")
    e.text = value
    result = types_factory.from_xcal("X-SOMETIME", e)
    assert isinstance(result, vTime)
    assert result.dt == expected.dt


@pytest.mark.parametrize(
    "invalid", [None, "", "123000", "12:30", "12:30:00+01:00", "INVALID", "1:30:00"]
)
def test_invalid_value_from_xcal(x_sometime, types_factory: TypesFactory, invalid):
    """Parse from xcal with an invalid value."""
    e = ET.Element("time")
    e.text = invalid
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("X-SOMETIME", e)
    assert error.value.parser == vTime
