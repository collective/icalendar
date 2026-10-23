"""A TZID that names a time zone equivalent to UTC must not end up next to a ``Z``.

:rfc:`5545#section-3.3.5` says:

.. code-block:: text

    The "TZID" property parameter MUST NOT be applied to DATE-TIME
    properties whose time values are specified in UTC.

Since 6.1.3, a time parsed with ``TZID=Etc/UTC`` (or another zone
equivalent to UTC) is written back with a ``Z`` but keeps its ``TZID``.

See https://github.com/collective/icalendar/issues/2020
"""

from datetime import datetime, timedelta

import pytest

from icalendar import Calendar, Parameters

ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//icalendar//test//EN
BEGIN:VEVENT
UID:utc-equivalent-tzid
DTSTAMP:20261023T120000Z
DTSTART;TZID={tzid}:20271105T090000
DTEND;TZID={tzid}:20271105T100000
END:VEVENT
END:VCALENDAR
"""

UTC_EQUIVALENT = pytest.mark.parametrize(
    "tzid",
    ["Etc/UTC", "GMT", "Etc/Greenwich", "Africa/Abidjan", "Atlantic/Reykjavik"],
)


def content_lines(tzid: str) -> list[str]:
    calendar = Calendar.from_ical(ICS.format(tzid=tzid))
    return [
        line
        for line in calendar.to_ical().decode().splitlines()
        if line.startswith(("DTSTART", "DTEND"))
    ]


@UTC_EQUIVALENT
def test_tzid_and_utc_are_not_combined(tzp, tzid):
    """The TZID parameter and the ``Z`` suffix exclude each other."""
    for line in content_lines(tzid):
        assert not (";TZID=" in line and line.endswith("Z")), line


@UTC_EQUIVALENT
def test_the_time_survives_the_round_trip(tzp, tzid):
    """Whichever form is written, it is read back as the same moment."""
    calendar = Calendar.from_ical(ICS.format(tzid=tzid))
    again = Calendar.from_ical(calendar.to_ical())
    start = again.events[0].start
    assert start.utcoffset() == timedelta(0)
    assert start.replace(tzinfo=None) == datetime(2027, 11, 5, 9, 0)


@UTC_EQUIVALENT
def test_jcal_has_no_tzid_next_to_z(tzp, tzid):
    """The jCal form leaves out the TZID as well."""
    calendar = Calendar.from_ical(ICS.format(tzid=tzid))
    _, params, _, value = calendar.events[0]["DTSTART"].to_jcal("dtstart")
    assert "tzid" not in params
    assert value.endswith("Z")


@UTC_EQUIVALENT
def test_parameters_know_the_tzid_is_utc(tzid):
    assert Parameters({"TZID": tzid}).is_utc()


def test_a_tzid_that_is_not_utc_is_not_utc():
    assert not Parameters({"TZID": "Europe/London"}).is_utc()


@UTC_EQUIVALENT
def test_no_vtimezone_is_added_for_it(tzp, tzid):
    """Nothing in the output refers to the time zone any more."""
    calendar = Calendar.from_ical(ICS.format(tzid=tzid))
    calendar.add_missing_timezones()
    assert not calendar.timezones


def test_a_historical_offset_is_converted(tzp):
    """Before 1912, Africa/Abidjan was 16 minutes behind UTC.

    A time written with a ``Z`` must be the moment in UTC, not the local time.
    """
    calendar = Calendar.from_ical(
        ICS.format(tzid="Africa/Abidjan").replace("2027110", "1900010")
    )
    start = calendar.events[0].start
    again = Calendar.from_ical(calendar.to_ical()).events[0].start
    assert again == start
