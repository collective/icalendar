"""xCal conversion for text-based values."""

from xml.etree import ElementTree as ET

import pytest

from icalendar import TypesFactory, vText, vUid
from icalendar.tests.rfc_6321_xcal.common import to_xcal

mark_text = pytest.mark.parametrize(
    "text", ["", "normal text", "中文鍵盤/中文键盘", "Text\nwith\nnewlines"]
)

mark_text_class = pytest.mark.parametrize("text_class", [vText, vUid])


@mark_text
@mark_text_class
def test_to_xcal(text, text_class):
    """Convert text-based values to xCal."""
    value = text_class(text)
    element = to_xcal(value)

    assert isinstance(element, ET.Element)
    assert element.tag == value.default_value
    assert element.text == text


@mark_text
def test_from_xcal_from_factory(types_factory: TypesFactory, text):
    """Parse text from xCal through the type factory."""
    element = ET.Element("text")
    element.text = text

    result = types_factory.from_xcal("x-prop", element)

    assert isinstance(result, vText)
    assert result.ical_value == text


@mark_text
@mark_text_class
def test_from_xcal_from_text_class(text, text_class):
    """Parse text-based values from xCal."""
    element = ET.Element("text")
    element.text = text

    result = text_class.from_xcal(element)

    assert isinstance(result, text_class)
    assert result.ical_value == text


@mark_text_class
def test_invalid_value_from_xcal(text_class):
    """Parse an empty xCal value."""
    element = ET.Element("text")

    result = text_class.from_xcal(element)

    assert result.ical_value == ""
