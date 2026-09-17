"""boolean converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.3
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vCalAddress
from icalendar.prop.factory import TypesFactory


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (vCalAddress("mailto:user@example.com"), "mailto:user@example.com"),
        (vCalAddress("mailto:john@doe.eu"), "mailto:john@doe.eu"),
    ],
)
def test_to_xcal(value, expected):
    """Convert to xcal."""
    e = value.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "cal-address"
    assert e.text == expected
    assert (
        ET.tostring(e, encoding="unicode") == f"<cal-address>{expected}</cal-address>"
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("mailto:user@example.com", vCalAddress("mailto:user@example.com")),
        ("mailto:john@doe.eu", vCalAddress("mailto:john@doe.eu")),
    ],
)
def test_from_xcal(types_factory: TypesFactory, value, expected):
    """Parse from xcal."""
    e = ET.Element("cal-address")
    e.text = value
    result = types_factory.from_xcal("x-prop", e)
    assert isinstance(result, vCalAddress)
    assert result == expected


def test_empty_value_should_not_fail():
    """Parse from xcal with empty value.

    That could also fail but then with the correct error.
    Consistency: We do not check formatting of these addresses.
    """
    e = ET.Element("cal-address")
    result = vCalAddress.from_xcal(e)
    assert isinstance(result, vCalAddress)
    assert result == vCalAddress("")
