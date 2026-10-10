"""binary conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.1
https://www.w3.org/TR/xmlschema-2/#base64Binary
"""

import sys
from xml.etree import ElementTree as ET

import pytest

from icalendar import vBinary
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory
from icalendar.tests.rfc_6321_xcal.common import XML_WHITESPACE, to_xcal

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
    e = to_xcal(vBinary(raw))
    assert isinstance(e, ET.Element)
    assert e[1].tag == "binary"
    assert e[1].text == value


@mark_values
def test_from_xcal(types_factory: TypesFactory, value, raw):
    """Parse from xcal."""
    e = ET.Element("binary")
    e.text = value
    result = vBinary.from_xcal(e)
    assert isinstance(result, vBinary)
    assert result.bytes == raw


def test_whitespace_is_ignored(types_factory: TypesFactory):
    """xsd:base64Binary may contain whitespace between the characters."""
    e = ET.Element("binary")
    e.text = XML_WHITESPACE + "VGhl IHF1aWNr" + XML_WHITESPACE
    assert vBinary.from_xcal(e).bytes == b"The quick"


INVALID_VALUES = ["INVALID!", "a"]

if sys.version_info >= (3, 12):
    INVALID_VALUES.append("MTIz=")


@pytest.mark.parametrize("invalid", INVALID_VALUES)
def test_invalid_value_from_xcal(types_factory: TypesFactory, invalid):
    """Parse from xcal with an invalid value."""
    e = ET.Element("binary")
    e.text = invalid
    with pytest.raises(XCalParsingError) as error:
        vBinary.from_xcal(e)
    assert error.value.message == "Expected base64 encoded data in /binary."


def test_round_trip_of_non_utf8_bytes():
    """Binary data that is not text must survive the conversion."""
    value = vBinary(bytes(range(256)))
    assert vBinary.from_xcal(to_xcal(value)).bytes == value.bytes
