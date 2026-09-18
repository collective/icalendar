"""Duplicated singleton UTC properties return the earliest value.

See https://github.com/collective/icalendar/issues/1795
"""

from datetime import date, datetime, timezone

import pytest

from icalendar import Calendar, Event, is_utc
from icalendar.error import InvalidCalendar
from icalendar.prop import vDDDTypes

UTC = timezone.utc


def test_issue_example_returns_earliest_dtstamp(tzp):
    """The exact calendar from the issue returns the earliest DTSTAMP.

    The earliest timestamp is not the first one encountered,
    proving earliest wins over first encountered.
    """
    c = Calendar.from_ical(
        """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTAMP:20210205T101751Z
UID:20200516T060000Z-123401@example.com
DTSTAMP:20200516T060000Z
SUMMARY:Do the needful
DTSTART:20220517T060000Z
DTEND:20220517T230000Z
RECURRENCE-ID:20220517T060000Z
END:VEVENT
END:VCALENDAR"""
    )
    assert c.events[-1].stamp == datetime(2020, 5, 16, 6, 0, tzinfo=UTC)


def test_single_dtstamp_is_unchanged(tzp):
    """A single DTSTAMP keeps its existing behavior."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    assert event.stamp == datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)


@pytest.mark.parametrize("earliest_first", [True, False])
def test_duplicate_utc_dtstamps_return_earliest(tzp, earliest_first):
    """Order of occurrence does not matter, the earliest value wins."""
    early = datetime(2020, 5, 16, 6, 0, tzinfo=UTC)
    late = datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)
    event = Event()
    first, second = (early, late) if earliest_first else (late, early)
    event.add("DTSTAMP", first)
    event.add("DTSTAMP", second)
    assert event.stamp == early


def test_duplicate_with_other_timezone_returns_earliest_instant(tzp):
    """A wall time in another timezone loses to an earlier instant in UTC."""
    utc_noon = datetime(2021, 1, 1, 12, 0, tzinfo=UTC)
    new_york_half_past_six = vDDDTypes(
        tzp.localize(datetime(2021, 1, 1, 6, 30), "America/New_York")
    )
    event = Event()
    event.add("DTSTAMP", utc_noon)
    event["DTSTAMP"] = [event["DTSTAMP"], new_york_half_past_six]
    assert event.stamp == datetime(2021, 1, 1, 11, 30, tzinfo=UTC)
    assert is_utc(event.stamp)


def test_duplicate_with_date_returns_earliest_after_midnight_utc(tzp):
    """A date counts as midnight UTC and can be the earliest value."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 1, 1, 12, 0, tzinfo=UTC))
    event["DTSTAMP"] = [vDDDTypes(date(2021, 1, 1)), event["DTSTAMP"]]
    assert event.stamp == datetime(2021, 1, 1, 0, 0, tzinfo=UTC)


def test_duplicate_with_naive_datetime_treats_it_as_utc(tzp):
    """A floating datetime is treated as UTC, like single values are."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 1, 1, 7, 0, tzinfo=UTC))
    event["DTSTAMP"] = [vDDDTypes(datetime(2021, 1, 1, 6, 0)), event["DTSTAMP"]]
    assert event.stamp == datetime(2021, 1, 1, 6, 0, tzinfo=UTC)


def test_duplicate_created_returns_earliest(tzp):
    """The leniency applies to other single UTC properties, too."""
    event = Event()
    event.add("CREATED", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event.add("CREATED", datetime(2020, 5, 16, 6, 0, tzinfo=UTC))
    assert event.CREATED == datetime(2020, 5, 16, 6, 0, tzinfo=UTC)


def test_invalid_item_still_raises(tzp):
    """An item that cannot be a datetime keeps raising InvalidCalendar."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event["DTSTAMP"] = [event["DTSTAMP"], 42]
    with pytest.raises(InvalidCalendar, match="DTSTAMP must be a datetime in UTC"):
        event.stamp


def test_empty_list_still_raises(tzp):
    """An empty value list stays invalid, as before."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event["DTSTAMP"] = []
    with pytest.raises(InvalidCalendar, match="DTSTAMP must be a datetime in UTC"):
        event.stamp
