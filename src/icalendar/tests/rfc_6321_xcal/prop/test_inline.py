"""inline conversion

vInline holds raw unparsed text, so it uses the <unknown> value element,
see https://datatracker.ietf.org/doc/html/rfc6321#section-3.6
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop import vInline

mark_values = pytest.mark.parametrize(
    "value", ["", "some text", "a;b:c", "TENTATIVE"]
)


@mark_values
def test_to_xcal(value):
    """Convert to xcal."""
    e = vInline(value).to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "unknown"
    assert e.text == value


@mark_values
def test_round_trip(value):
    """Parse back what was written."""
    result = vInline.from_xcal(vInline(value).to_xcal())
    assert isinstance(result, vInline)
    assert result == value


def test_an_empty_element_is_an_empty_value():
    """<unknown/> has no text."""
    assert vInline.from_xcal(ET.Element("unknown")) == ""


def test_a_line_break_is_invalid():
    """An inline value may not contain CR or LF characters."""
    e = ET.Element("unknown")
    e.text = "one\ntwo"
    with pytest.raises(XCalParsingError) as error:
        vInline.from_xcal(e)
    assert error.value.parser == vInline
