"""uri conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.13
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vUri
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory

mark_values = pytest.mark.parametrize(
    "value",
    [
        "http://example.com/my-report.txt",
        "mailto:jane_doe@example.com",
        "ftp://example.com/pub/calendars/jsmith/mytime.ics",
        "CID:jsmith.part3.960817T083000.xyzMail@example.com",
    ],
)


@mark_values
def test_to_xcal(value):
    """Convert to xcal."""
    e = vUri(value).to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "uri"
    assert e.text == value
    assert ET.tostring(e, encoding="unicode") == f"<uri>{value}</uri>"


@mark_values
def test_from_xcal(types_factory: TypesFactory, value):
    """Parse from xcal."""
    e = ET.Element("uri")
    e.text = value
    result = types_factory.from_xcal("url", e)
    assert isinstance(result, vUri)
    assert result == vUri(value)


def test_empty_element_from_xcal(types_factory: TypesFactory):
    """An <uri/> element without text carries no URI."""
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("url", ET.Element("uri"))
    assert error.value.parser == vUri
    assert error.value.message == "Expected a URI. Got None in 'uri' element parsing 'vUri'."


def test_uri_with_a_line_break_from_xcal(types_factory: TypesFactory):
    """A URI may not contain CR or LF characters."""
    e = ET.Element("uri")
    e.text = "http://example.com/my\nreport.txt"
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("url", e)
    assert error.value.parser == vUri
