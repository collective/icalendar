"""Parse the calendar and make sure the timezone is used.

See https://github.com/collective/icalendar/issues/218
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from icalendar.cal.timezone import TimezoneDaylight, TimezoneStandard
from icalendar.timezone.tzid import tzid_from_dt

if TYPE_CHECKING:
    from calendar import Calendar

    from icalendar.cal.event import Event


@pytest.fixture
def event(calendars) -> Event:
    """The event to check."""
    return calendars.issue_218_bad_tzid.events[0]


def test_event_has_start_and_end(event: Event):
    """The calendar should be parsed and the start and end have a timezone."""
    assert event.start.replace(tzinfo=None) == datetime(2017, 2, 28, 23, 00)
    assert event.end.replace(tzinfo=None) == datetime(2017, 2, 28, 23, 30)


def test_timezone(event: Event):
    """The event uses a timezone."""
    assert event.start.tzinfo == event.end.tzinfo
    assert tzid_from_dt(event.start) == "UTC+11"
    assert event.start.utcoffset() == timedelta(hours=11)


def test_dtstart_of_timezone_is_datetime(calendars):
    """Test the failing test case and try to narrow down the problem."""
    calendar: Calendar = calendars.issue_218_bad_tzid
    print(calendar.raw_ics.decode())
    print(calendar.to_ical().decode())
    tz = calendar.timezones[0]
    assert tz["TZID"] == "UTC+11"
    standard = tz.standard[0]
    assert standard["DTSTART"].dt == date(2017, 1, 1)
    assert standard["DTSTART"].params.value == "DATE"
    assert standard.DTSTART == datetime(2017, 1, 1)


@pytest.mark.parametrize("TZ", [TimezoneStandard, TimezoneDaylight])
def test_setter_of_timezone_start(TZ):
    """The setter received conversion functionality."""
    tz = TZ()
    tz.DTSTART = date(2017, 1, 1)
    assert tz.DTSTART == datetime(2017, 1, 1)
    assert tz["DTSTART"].params == {}
