from datetime import datetime, timezone

import pytest

from icalendar import Calendar
from icalendar.prop import vDDDLists, vPeriod
from icalendar.prop.broken import vBroken


def test_zero_length_period_identical_datetimes_rejected():
    start = datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="Start time is equal to end time"):
        vPeriod((start, start))


def test_zero_length_period_from_ical_rejected():
    with pytest.raises(ValueError, match="Start time is equal to end time"):
        vPeriod.from_ical("20261110T100000Z/20261110T100000Z")


def test_zero_length_period_in_vdddlists_rejected():
    with pytest.raises(ValueError, match="Start time is equal to end time"):
        vDDDLists.from_ical("20261110T100000Z/20261110T100000Z")


def test_zero_length_period_in_calendar_marked_broken():
    ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//example//test//EN
BEGIN:VEVENT
UID:zero-period
DTSTART:20261110T100000Z
RDATE;VALUE=PERIOD:20261110T100000Z/20261110T100000Z
END:VEVENT
END:VCALENDAR
"""
    cal = Calendar.from_ical(ics)
    rdate = cal.subcomponents[0]["RDATE"]
    assert isinstance(rdate, vBroken)
    assert isinstance(rdate.parse_error, ValueError)
    assert "Start time is equal to end time" in str(rdate.parse_error)
