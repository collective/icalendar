"""Check that we convert the examples propertly."""

from pprint import pprint

import pytest

from icalendar.cal.event import Event
from icalendar.parser_tools import to_unicode
from icalendar.prop import vText


def test_convert_coffee(calendars):
    """convert the unknown value property"""
    calendar = calendars.rfc_7265_unknown_parameter
    ical = calendar.to_ical().decode()
    print(to_unicode(ical))
    assert r"X-COFFEE-DATA:Stenophylla;Guinea\\\,Africa" in ical


@pytest.mark.parametrize(
    ("prop_name", "value", "expected_value"),
    [
        ("SUMMARY", "TEXT", "TEXT"),
        ("SUMMARY", "URI", "URI"),
        ("DESCRIPTION", "URI", "URI"),
        ("X-ALT-DESC", "UNKNOWN", "UNKNOWN"),
        ("X-ALT-DESC", "TEXT", "UNKNOWN"),
        ("DESCRIPTION", "TEXT", "TEXT"),
    ],
)
def test_know_attributes_do_not_receive_a_VALUE(prop_name, value, expected_value):
    """If we do not know a certain attribute, we always use the unknown property type."""
    event = Event()
    prop = vText("XXX")
    prop.VALUE = value
    event[prop_name] = prop
    jcal = event.to_jcal()
    pprint(jcal)
    event2 = Event.from_jcal(jcal)
    pprint(event2.to_jcal())
    assert event2[prop_name].VALUE == expected_value
