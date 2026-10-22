"""Component names must be valid iCalendar tokens.

A component name is an ``iana-token`` or ``x-name`` (RFC 5545 section 3.6).
The parser used to accept any ``BEGIN`` value and :meth:`Component.to_xcal`
then used it verbatim as the XML element name, so a name containing ``<`` or
``>`` injected elements into the xCal output.
"""

import pytest

from icalendar import (
    Calendar,
    ComponentFactory,
    ICalParsingError,
    LazyCalendar,
    XCalParsingError,
)

INVALID_COMPONENT_NAMES = [
    "X-A><INJECTED/><X-A",
    "X-A B",
    "VEVENT;X=1",
    "X-A:B",
    'X-A"B',
    "",
    " X-A",
    "X-A ",
    "X-A\tB",
    "X-A\x0bB",
    "X-A\xa0B",
    "X-A\u3000B",
    "X-A\x00",
    "X-A\x7f",
]

VALID_COMPONENT_NAMES = ["X-VENDOR-COMP", "x-lower", "X-1.2_3", "VEVENT"]


def calendar_with_component(name: str) -> str:
    """Return a calendar containing a component with the given name."""
    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:x\r\n"
        f"BEGIN:{name}\r\n"
        "UID:1\r\n"
        f"END:{name}\r\n"
        "END:VCALENDAR\r\n"
    )


@pytest.mark.parametrize("name", INVALID_COMPONENT_NAMES)
@pytest.mark.parametrize("calendar_class", [Calendar, LazyCalendar])
def test_invalid_component_name_is_rejected(calendar_class, name):
    """A component name that is not a valid token raises a parsing error."""
    with pytest.raises(
        ICalParsingError,
        match=r"The component name must be a valid iCalendar token",
    ):
        calendar_class.from_ical(calendar_with_component(name))


@pytest.mark.parametrize("name", INVALID_COMPONENT_NAMES)
def test_invalid_top_level_component_name_is_rejected(name):
    """The name of the top-level component is checked as well."""
    with pytest.raises(ICalParsingError):
        Calendar.from_ical(f"BEGIN:{name}\r\nEND:{name}\r\n")


@pytest.mark.parametrize("name", VALID_COMPONENT_NAMES)
def test_valid_component_name_round_trips_through_xcal(name):
    """A valid custom component name is parsed and produces well-formed xCal."""
    calendar = Calendar.from_ical(calendar_with_component(name))
    assert calendar.subcomponents[0].name == name.upper()
    xcal = calendar.to_xcal()
    assert Calendar.from_xcal(xcal)[0].subcomponents[0].name == name.upper()


@pytest.mark.parametrize("name", INVALID_COMPONENT_NAMES)
def test_component_factory_rejects_invalid_name(name):
    """The component factory does not create a class for an invalid name."""
    factory = ComponentFactory()
    with pytest.raises(ValueError):
        factory.get_component_class(name)
    assert name not in factory


def test_invalid_xcal_component_name_is_rejected():
    """An XML element name that is not a valid token is rejected."""
    xcal = (
        '<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">'
        "<vcalendar><components><x-a\u00b7b/></components></vcalendar>"
        "</icalendar>"
    ).encode()
    with pytest.raises(
        XCalParsingError,
        match=r"The component name must be a valid iCalendar token",
    ):
        Calendar.from_xcal(xcal)
