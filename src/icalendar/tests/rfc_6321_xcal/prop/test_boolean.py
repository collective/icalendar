"""boolean converison

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.2
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vBoolean
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory
from icalendar.tests.rfc_6321_xcal.common import to_xcal


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (vBoolean(True), "true"),
        (vBoolean(False), "false"),
    ],
)
def test_to_xcal(value, expected):
    """Convert to xcal."""
    e = to_xcal(value)
    assert isinstance(e, ET.Element)
    assert e.tag == "boolean"
    assert e.text == expected
    assert ET.tostring(e, encoding="unicode") == f"<boolean>{expected}</boolean>"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", vBoolean(True)),
        ("false", vBoolean(False)),
    ],
)
def test_from_xcal(types_factory: TypesFactory, value, expected):
    """Parse from xcal."""
    e = ET.Element("boolean")
    e.text = value
    result = types_factory.from_xcal("x-prop", e)
    assert isinstance(result, vBoolean)
    assert result == expected


def test_invalid_value_from_xcal(types_factory: TypesFactory):
    """Parse from xcal with invalid value."""
    e = ET.Element("boolean")
    e.text = "INVALID"
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("x-prop", e)
    assert error.value.parser == vBoolean
    assert (
        error.value.message
        == "Expected 'true' or 'false'. Got 'INVALID' in 'boolean' element parsing 'vBoolean'."
    )
