"""binary conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.1
https://www.w3.org/TR/xmlschema-2/#base64Binary
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vBinary
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory

from .common import XML_WHITESPACE

mark_values = pytest.mark.parametrize(
    ("value", "raw"),
    [
        ("", b""),
        ("MTIz", b"123"),
        ("VGhlIHF1aWNrIGJyb3duIGZveA==", b"The quick brown fox"),
        ("//79", b"\xff\xfe\xfd"),
    ],
)


@mark_values
def test_to_xcal(value, raw):
    """Convert to xcal."""
    e = vBinary(raw).to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "binary"
    assert e.text == value


@mark_values
def test_from_xcal(types_factory: TypesFactory, value, raw):
    """Parse from xcal."""
    e = ET.Element("binary")
    e.text = value
    result = types_factory.from_xcal("attach", e)
    assert isinstance(result, vBinary)
    assert result.bytes == raw


def test_whitespace_is_ignored(types_factory: TypesFactory):
    """xsd:base64Binary may contain whitespace between the characters."""
    e = ET.Element("binary")
    e.text = XML_WHITESPACE + "VGhl IHF1aWNr" + XML_WHITESPACE
    assert types_factory.from_xcal("attach", e).bytes == b"The quick"


@pytest.mark.parametrize("invalid", ["INVALID!", "MTIz=", "a"])
def test_invalid_value_from_xcal(types_factory: TypesFactory, invalid):
    """Parse from xcal with an invalid value."""
    e = ET.Element("binary")
    e.text = invalid
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("attach", e)
    assert error.value.parser == vBinary


def test_round_trip_of_non_utf8_bytes():
    """Binary data that is not text must survive the conversion."""
    value = vBinary(bytes(range(256)))
    assert vBinary.from_xcal(value.to_xcal()).bytes == value.bytes
