"""Test getting elements from an xCal element."""

from xml.etree.ElementTree import Element, ParseError

import pytest

from icalendar.cal.calendar import Calendar
from icalendar.cal.component import Component
from icalendar.error import XCalParsingError

from .common import _xcal


def test_component_from_xcal_chooses_correct_type(component: Component):
    """The component factory is used to get the right type."""
    c = component.from_xcal(_xcal(component))
    assert isinstance(c, Component)
    assert c.name == component.name


def test_input_can_be_a_file(calendars):
    """The file interface can be used."""
    cal = calendars.rfc_7265_appendix_example_1_xcal.source_path.open("rb")
    c = Component.from_xcal(cal)
    assert c.name == "VCALENDAR"
    assert isinstance(c, Calendar)


def test_input_can_be_an_element():
    """The Element interface can be used."""
    e = Element("vcalendar")
    c = Component.from_xcal(e)
    assert c.name == "VCALENDAR"
    assert isinstance(c, Calendar)


def test_input_can_be_a_path(calendars):
    """The path interface can be used."""
    cal = calendars.rfc_7265_appendix_example_1_xcal.source_path
    c = Component.from_xcal(cal)
    assert c.name == "VCALENDAR"
    assert isinstance(c, Calendar)


def test_input_can_be_bytes():
    """The string interface can be used."""
    pytest.skip("TODO")


def test_input_can_not_be_a_string():
    """The string interface can be used."""
    with pytest.raises(TypeError):
        Component.from_xcal("")


@pytest.mark.parametrize(
    ("xml"),
    [
        (b""),
        (b'<?xml version="1.0" encoding="utf-8" ?>'),
    ],
)
def test_invalid_xml_input_raises_error(xml):
    """An empty input should be considered."""
    with pytest.raises(ParseError):
        Component.from_xcal(xml)


@pytest.mark.parametrize(
    ("xml", "message"),
    [
        (
            b'<?xml version="1.0" encoding="utf-8" ?>\n<icalendar />',
            "Namespace is missing content. Got None in 'icalendar' element parsing 'Component'.",
        ),
    ],
)
def test_invalid_xcal_input_raises_error(xml, message):
    """An empty input should be considered."""
    with pytest.raises(XCalParsingError) as error:
        Component.from_xcal(xml)
    assert error.value.parser == Component
    assert error.value.message == message
