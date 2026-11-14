"""Ignore foreign elements below properties (RFC 6321 section 4.1)."""

from datetime import date
from xml.etree.ElementTree import fromstring

import pytest

from icalendar import Event
from icalendar.parser.xcal.base import XCalParser


@pytest.mark.parametrize("name", ["extra", "text", "parameters"])
@pytest.mark.parametrize("position", ["before", "after"])
def test_foreign_property_children_are_ignored(name, position):
    """Foreign children cannot add values or impersonate iCalendar tags."""
    foreign = f"<c:{name}>Ignored</c:{name}>"
    children = [foreign, "<text>Agenda</text>"]
    if position == "after":
        children.reverse()
    event = Event.from_xcal(
        fromstring(
            '<vevent xmlns="urn:ietf:params:xml:ns:icalendar-2.0" '
            'xmlns:c="http://example.com/custom-ns"><properties><description>'
            + "".join(children)
            + "</description></properties></vevent>"
        )
    )[0]
    assert event.to_ical() == b"BEGIN:VEVENT\r\nDESCRIPTION:Agenda\r\nEND:VEVENT\r\n"


def test_foreign_parameter_children_are_ignored():
    """Foreign elements cannot become parameters or parameter values."""
    event = Event.from_xcal(
        fromstring(
            '<vevent xmlns="urn:ietf:params:xml:ns:icalendar-2.0" '
            'xmlns:c="http://example.com/custom-ns"><properties><attendee>'
            "<parameters><c:cn><text>Ignored</text></c:cn>"
            "<cn><c:text>Ignored</c:text><text>Person</text></cn></parameters>"
            "<cal-address>mailto:person@example.com</cal-address>"
            "</attendee></properties></vevent>"
        )
    )[0]
    assert event["ATTENDEE"].params == {"CN": "Person"}


def test_unknown_icalendar_value_is_preserved():
    """Unknown value types in the iCalendar namespace still round-trip."""
    event = Event.from_xcal(
        fromstring(
            '<vevent xmlns="urn:ietf:params:xml:ns:icalendar-2.0">'
            "<properties><x-example><custom>Value</custom></x-example></properties>"
            "</vevent>"
        )
    )[0]
    assert b"X-EXAMPLE;VALUE=CUSTOM:Value\r\n" in event.to_ical()


def test_direct_property_extensions_remain_available_to_parser():
    """Direct children of properties are reserved for XML extension handling."""
    parser = XCalParser(
        fromstring(
            '<properties xmlns:c="http://example.com/custom-ns"><c:extra/></properties>'
        )
    )
    assert parser.child.element.tag == "{http://example.com/custom-ns}extra"


@pytest.mark.parametrize(
    ("property_xml", "expected"),
    [
        (
            "<geo><geo><c:latitude>99</c:latitude><latitude>1</latitude>"
            "<c:longitude>99</c:longitude><longitude>2</longitude></geo></geo>",
            b"GEO:1.0;2.0\r\n",
        ),
        (
            "<freebusy><period><c:start>2000-01-01T00:00:00Z</c:start>"
            "<start>2026-01-01T00:00:00Z</start>"
            "<c:end>2000-01-01T01:00:00Z</c:end>"
            "<end>2026-01-01T01:00:00Z</end></period></freebusy>",
            b"FREEBUSY:20260101T000000Z/20260101T010000Z\r\n",
        ),
    ],
)
def test_foreign_elements_inside_structured_values_are_ignored(property_xml, expected):
    """Nested semantic lookups must also respect XML namespaces."""
    event = Event.from_xcal(
        fromstring(
            '<vevent xmlns="urn:ietf:params:xml:ns:icalendar-2.0" '
            'xmlns:c="http://example.com/custom-ns"><properties>'
            + property_xml
            + "</properties></vevent>"
        )
    )[0]
    assert expected in event.to_ical()


def test_foreign_children_do_not_change_recurrence_date_parsing():
    """A foreign child does not turn a plain date into a structured value."""
    event = Event.from_xcal(
        fromstring(
            '<vevent xmlns="urn:ietf:params:xml:ns:icalendar-2.0" '
            'xmlns:c="http://example.com/custom-ns"><properties><rrule><recur>'
            "<freq>DAILY</freq><until>2026-01-01<c:extra>Ignored</c:extra></until>"
            "</recur></rrule></properties></vevent>"
        )
    )[0]
    assert event["RRULE"]["UNTIL"] == [date(2026, 1, 1)]
