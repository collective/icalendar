"""Testing functionality that is common to date and time property types."""

from datetime import datetime, time

import pytest

from icalendar import Component, vDatetime, vDDDLists, vDDDTypes, vTime
from icalendar.compatibility import ZoneInfo
from icalendar.parser_tools import to_unicode
from icalendar.prop import VPROPERTY


@pytest.fixture(
    params=[
        vDatetime(datetime(2018, 1, 1, tzinfo=ZoneInfo("UTC"))),
        vTime(time(1, 1, tzinfo=ZoneInfo("UTC"))),
    ]
)
def utc_prop(request):
    return request.param


@pytest.mark.parametrize("convert", [None, vDDDLists, vDDDTypes])
def test_setting_a_utc_datetime_value_does_not_include_a_TZID(
    utc_prop: VPROPERTY, convert
):
    """Check that the VALUE parameter is correctly determined."""
    if convert:
        utc_prop = convert(utc_prop.dt)
    assert utc_prop.params.is_utc()
    component = Component()
    component.add("X-PROP", utc_prop)
    component.add("DTSTAMP", utc_prop)
    component.add("DTSTART", utc_prop)
    component.add("DUE", utc_prop)

    ical = component.to_ical().decode()
    print(ical)
    assert "TZID" not in ical


def test_converting_to_utc_puts_a_z_in_the_end(utc_prop: VPROPERTY):
    """Test that the Z is appended.

    :rfc:`5545`, TIME:
        UTC time, or absolute time, is identified by a LATIN CAPITAL
        LETTER Z suffix character, the UTC designator, appended to the
        time value.  For example, the following represents 07:00 AM UTC:

        .. code-block:: text

            070000Z

        The "TZID" property parameter MUST NOT be applied to TIME
        properties whose time values are specified in UTC.

    :rfc:`5545`, DATE-TIME:
        The date with UTC time, or absolute time, is identified by a LATIN
        CAPITAL LETTER Z suffix character, the UTC designator, appended to
        the time value.  For example, the following represents January 19,
        1998, at 0700 UTC:

        .. code-block:: text

            19980119T070000Z

        The "TZID" property parameter MUST NOT be applied to DATE-TIME
        properties whose time values are specified in UTC.

    """
    ical = to_unicode(utc_prop.to_ical())
    assert ical.endswith("Z")
