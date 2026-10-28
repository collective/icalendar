"""Special cases for not having any value.

This means no value has been assigned and the calendar is invalid.
The parameters still should be preserved.

Examples:

    .. code-block:: xcal

        <properties>
            <x-prop>
            </x-prop>
        </properties>

    .. code-block:: jcal

        [
            "x-prop", {},
        ]

    .. code-block:: ical

        BEGIN:VEVENT
        XPROP
        END:VEVENT
"""

from xml.etree.ElementTree import indent, tostring

import pytest

from icalendar.cal.calendar import Calendar
from icalendar.cal.event import Event
from icalendar.error import InvalidCalendar
from icalendar.tests.rfc_6321_xcal.common import list2xml


@pytest.mark.parametrize("prop_name", ["summary", "x-prop", "dtstart"])
@pytest.mark.parametrize("has_text", [False, True])
def test_just_an_empty_property_is_invalid_and_does_not_turn_up(prop_name, has_text):
    """Test that the property is there.

    We have an empty property.
    """
    xml = list2xml(["vevent", ["properties", [prop_name] + ["      "] * has_text]])
    indent(xml)
    print(tostring(xml))
    event = Event.from_xcal(xml)[0]
    assert prop_name not in event


@pytest.mark.parametrize("prop_name", ["summary", "x-prop", "dtstart"])
def test_property_without_value_preserves_parameters(prop_name):
    """Test that the property is there.

    We have an empty property.
    """
    xml = list2xml(
        [
            "vevent",
            ["properties", [prop_name, ["parameters", ["x-param", ["text", "123"]]]]],
        ]
    )
    indent(xml)  # important, might change the value
    print("XML:", tostring(xml).decode())
    event = Event.from_xcal(xml)[0]
    assert event[prop_name] == ""
    with pytest.raises(InvalidCalendar):
        _ = event[prop_name].ical_value
    assert event[prop_name].params == {"X-PARAM": "123", "VALUE": "UNKNOWN"}


def test_value_is_empty_in_invalid_attribute(calendars):
    cal = calendars.issue_348_exception_parsing_value
    empty_value_from_incomplete_property = cal.subcomponents[0]["X-ORGANIZER2"]
    assert empty_value_from_incomplete_property == ""
    xml = cal.to_xcal(indent=1)
    print(xml.decode())
    copy_of_calendar = Calendar.from_xcal(xml)[0]
    xvalue = copy_of_calendar.subcomponents[0]["X-ORGANIZER2"]
    assert xvalue == ""
    xvalue.params.pop("VALUE", None)  # we make no promises about the VALUE parameter
    assert xvalue.params == empty_value_from_incomplete_property.params
