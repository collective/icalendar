"""Tests for the vRecur.until accessor."""

from datetime import date, datetime

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vDDDTypes, vRecur


def test_until_returns_none_when_absent():
    assert vRecur.from_ical("FREQ=DAILY").until is None


def test_until_returns_datetime():
    dt = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231T235959Z").until
    assert isinstance(dt, datetime)
    assert dt.year == 2026
    assert dt.month == 12
    assert dt.day == 31


def test_until_returns_date():
    d = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231").until
    assert isinstance(d, date)
    assert d.year == 2026
    assert d.month == 12
    assert d.day == 31


def test_until_returns_first_value_when_multiple_are_present():
    recur = vRecur(FREQ=["DAILY"], UNTIL=[vDDDTypes(date(2026, 12, 31)), vDDDTypes(date(2027, 1, 1))])
    assert recur.until == date(2026, 12, 31)


def test_until_returns_none_when_value_is_an_empty_list():
    recur = vRecur(FREQ=["DAILY"], UNTIL=[])
    assert recur.until is None


def test_setting_until_date_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.until = date(2026, 12, 31)
    assert recur.until == date(2026, 12, 31)
    assert recur.to_ical() == b"FREQ=DAILY;UNTIL=20261231"


def test_setting_until_datetime_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.until = datetime(2026, 12, 31, 23, 59, 59)
    assert recur.until == datetime(2026, 12, 31, 23, 59, 59)


def test_setting_until_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231")
    recur.until = None
    assert recur.until is None
    assert "UNTIL" not in recur


def test_deleting_until_removes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231")
    del recur.until
    assert recur.until is None
    assert "UNTIL" not in recur


def test_deleting_until_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.until
    assert recur.until is None


def test_setting_until_invalid_value_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.until = "invalid-date"


def test_until_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.until == date(2026, 12, 31)
