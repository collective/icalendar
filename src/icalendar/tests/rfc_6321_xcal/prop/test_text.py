"""date converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.4
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import TypesFactory, vText

mark_text = pytest.mark.parametrize(
    "text", ["", "normal text", "中文鍵盤/中文键盘", "Text\nwith\nnewlines"]
)


@mark_text
def test_to_xcal(text):
    """Convert to xcal."""
    v_text = vText(text)
    e = v_text.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "text"
    assert e.text == text


@mark_text
def test_from_xcal_from_factory(types_factory: TypesFactory, text):
    """Parse from xcal."""
    e = ET.Element("text")
    e.text = text
    result = types_factory.from_xcal("x-prop", e)
    assert isinstance(result, vText)
    assert result.ical_value == text


@mark_text
def test_from_xcal_from_v_text(text):
    """Parse from xcal."""
    e = ET.Element("text")
    e.text = text
    result = vText.from_xcal(e)
    assert isinstance(result, vText)
    assert result.ical_value == text


def test_invalid_value_from_xcal():
    """Parse from xcal with invalid value."""
    e = ET.Element("text")
    text = vText.from_xcal(e)
    assert text.ical_value == ""
