"""A TZID that names a time zone equivalent to UTC must not end up next to a ``Z``.

:rfc:`5545#section-3.3.5` says:

.. code-block:: text

    The "TZID" property parameter MUST NOT be applied to DATE-TIME
    properties whose time values are specified in UTC.

Since 6.1.3, a time parsed with ``TZID=Etc/UTC`` (or another zone
equivalent to UTC) is written back with a ``Z`` but keeps its ``TZID``.

Either form is correct: a ``Z`` without the ``TZID``, or the ``TZID``
with the local time and a VTIMEZONE.  The tests accept both, as keeping
the ``TZID`` of a place like ``Atlantic/Reykjavik`` keeps the information
that the time follows that place's rules, should they change.

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
    """The jCal form does not combine them either."""
    event = Calendar.from_ical(ICS.format(tzid=tzid)).events[0]
    for name, time in [("DTSTART", "09"), ("DTEND", "10")]:
        _, params, _, value = event[name].to_jcal(name.lower())
        if "tzid" in params:
            assert value == f"2027-11-05T{time}:00:00"
        else:
            assert value == f"2027-11-05T{time}:00:00Z"


def test_a_tzid_alone_does_not_decide_utc():
    """Whether a time in a zone equivalent to UTC is UTC depends on the time."""
    assert not Parameters({"TZID": "Etc/UTC"}).is_utc()


@UTC_EQUIVALENT
def test_a_vtimezone_is_added_only_for_a_tzid_in_use(tzp, tzid):
    """A VTIMEZONE is added if, and only if, the TZID is kept."""
    calendar = Calendar.from_ical(ICS.format(tzid=tzid))
    calendar.add_missing_timezones()
    used = {";TZID=" in line for line in content_lines(tzid)}
    assert used == {bool(calendar.timezones)}
    assert not calendar.get_missing_tzids()


@UTC_EQUIVALENT
def test_xcal_has_no_tzid_next_to_z(tzp, tzid):
    """The xCal form does not combine them either."""
    xcal = Calendar.from_ical(ICS.format(tzid=tzid)).to_xcal().decode()
    for tag, time in [("dtstart", "09"), ("dtend", "10")]:
        element = xcal[xcal.index(f"<{tag}>") : xcal.index(f"</{tag}>")]
        if "<tzid>" in element:
            assert f"<date-time>2027-11-05T{time}:00:00</date-time>" in element
        else:
            assert f"<date-time>2027-11-05T{time}:00:00Z</date-time>" in element


ICS_1900 = ICS.format(tzid="Africa/Abidjan").replace("2027110", "1900010")


def test_a_historical_offset_is_not_utc(tzp):
    """Before 1912, Africa/Abidjan was 16 minutes behind UTC.

    Then, it is a time zone like any other and keeps its TZID.
    """
    calendar = Calendar.from_ical(ICS_1900)
    ical = calendar.to_ical().decode()
    assert "DTSTART;TZID=Africa/Abidjan:19000105T090000" in ical.splitlines()
    again = Calendar.from_ical(ical).events[0].start
    assert again == calendar.events[0].start


def test_a_historical_offset_needs_a_vtimezone(tzp):
    calendar = Calendar.from_ical(ICS_1900)
    assert calendar.get_missing_tzids() == {"Africa/Abidjan"}


def test_a_historical_offset_in_xcal(tzp):
    xcal = Calendar.from_ical(ICS_1900).to_xcal().decode()
    assert "<tzid><text>Africa/Abidjan</text></tzid>" in xcal
    assert "<date-time>1900-01-05T09:00:00</date-time>" in xcal


def test_a_historical_offset_in_jcal(tzp):
    calendar = Calendar.from_ical(ICS_1900)
    _, params, _, value = calendar.events[0]["DTSTART"].to_jcal("dtstart")
    assert params["tzid"] == "Africa/Abidjan"
    assert value == "1900-01-05T09:00:00"


@pytest.mark.parametrize(
    "values", ["19130105T090000,19000105T090000", "19000105T090000,19130105T090000"]
)
def test_a_list_across_the_offset_change_keeps_its_tzid(tzp, values):
    """If only some times of a list are UTC, the TZID is still needed."""
    calendar = Calendar.from_ical(
        ICS_1900.replace(
            "END:VEVENT", f"EXDATE;TZID=Africa/Abidjan:{values}\r\nEND:VEVENT"
        )
    )
    exdate = calendar.events[0]["EXDATE"]
    again = Calendar.from_ical(calendar.to_ical()).events[0]["EXDATE"]
    assert [d.dt for d in again.dts] == [d.dt for d in exdate.dts]
