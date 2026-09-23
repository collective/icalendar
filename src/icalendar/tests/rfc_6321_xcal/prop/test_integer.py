"""integer conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.8
https://datypic.com/sc/xsd/t-xsd_integer.html
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vInt
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory

from .common import XML_WHITESPACE


@pytest.mark.parametrize(
    ("python", "xml", "message"),
    [
        (0, "0", ""),
        (-1234, "-1234", ""),
        (1234, "+1234", "leading plus is allowed"),
        (126, "126", ""),
        (0, "-0", "minus zero is zero"),
        (12, "00012", "leading zeros are allowed"),
        (12, XML_WHITESPACE + "12" + XML_WHITESPACE, "White Space: collapse"),
    ],
)
def test_xsd_integer_to_python(python, xml, message):
    """Convert to python.

    See https://datypic.com/sc/xsd/t-xsd_integer.html
    """
    assert vInt.from_xsd_integer(xml) == python, message


@pytest.mark.parametrize(
    ("python", "xml"),
    [(0, "0"), (-1234, "-1234"), (1234, "1234"), (126, "126")],
)
def test_python_to_xsd(python, xml):
    """Convert to xsd:integer.

    See https://datypic.com/sc/xsd/t-xsd_integer.html
    """
    assert vInt.to_xsd_integer(python) == xml


@pytest.mark.parametrize(
    "invalid_xml_value", ["", " ", "INVALID", "3.0", "1,234", "1 234", "12E3", None]
)
def test_parsing_errors(invalid_xml_value):
    """This tests invalid examples and asserts the correct error.

    See https://datypic.com/sc/xsd/t-xsd_integer.html
    """
    with pytest.raises((TypeError, ValueError)) as error:
        vInt.from_xsd_integer(invalid_xml_value)
    assert error.value.args[0] == (
        f"Expected xsd:integer. Got {invalid_xml_value!r}."
        if isinstance(invalid_xml_value, str)
        else "Expected xsd:integer. Got None."
    )


mark_values = pytest.mark.parametrize(
    ("value", "expected"),
    [("1000", vInt(1000)), ("-42", vInt(-42))],
)


@mark_values
def test_to_xcal(value, expected):
    """Convert to xcal."""
    e = expected.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "integer"
    assert e.text == value
    assert ET.tostring(e, encoding="unicode") == f"<integer>{value}</integer>"


@mark_values
def test_from_xcal(types_factory: TypesFactory, value, expected):
    """Parse from xcal."""
    e = ET.Element("integer")
    e.text = value
    result = types_factory.from_xcal("x-prop", e)
    assert isinstance(result, vInt)
    assert result == expected


def test_invalid_value_from_xcal(types_factory: TypesFactory):
    """Parse from xcal with invalid value."""
    e = ET.Element("integer")
    e.text = "INVALID"
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("x-prop", e)
    assert error.value.parser == vInt
    assert (
        error.value.message
        == "Expected xsd:integer. Got 'INVALID' in 'integer' element parsing 'vInt'."
    )
