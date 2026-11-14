from datetime import date, datetime, timezone

import pytest

from icalendar.prop import vRecur
from icalendar.tests.rfc_6321_xcal.common import list2xml


def test_until_returns_none_when_absent():
    """UNTIL is not set at all."""
    assert vRecur.from_ical("FREQ=DAILY").until is None


def test_until_returns_the_datetime_value():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231T235959Z")
    assert recur.until == datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


def test_until_returns_the_date_value():
    """UNTIL may be a DATE value, not only DATE-TIME."""
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231")
    assert recur.until == date(2026, 12, 31)


def test_until_returns_first_value_when_multiple_are_present():
    """If multiple values are given, the first one is returned."""
    recur = vRecur(FREQ=["DAILY"], UNTIL=[date(2026, 1, 1), date(2026, 2, 1)])
    assert recur.until == date(2026, 1, 1)


def test_until_returns_none_when_value_is_an_empty_list():
    """If an empty list is in there, None is returned."""
    recur = vRecur(FREQ=["DAILY"], UNTIL=[])
    assert recur.until is None


def test_setting_until_to_a_datetime_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.until = datetime(2027, 1, 1, tzinfo=timezone.utc)
    assert recur.until == datetime(2027, 1, 1, tzinfo=timezone.utc)
    assert recur.to_ical() == b"FREQ=DAILY;UNTIL=20270101T000000Z"


def test_setting_until_to_a_date_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.until = date(2027, 6, 15)
    assert recur.until == date(2027, 6, 15)
    assert recur.to_ical() == b"FREQ=DAILY;UNTIL=20270615"


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
    del recur.until  # should not raise
    assert recur.until is None


def test_setting_until_to_non_date_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.until = "20261231"


def test_setting_until_to_int_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.until = 20261231


def test_until_datetime_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231T235959Z")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.until == recur.until


def test_until_date_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=20261231")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.until == recur.until


def test_until_returns_a_raw_datetime_when_parsed_from_xcal():
    """A vRecur parsed from xCal exposes the same raw datetime through
    ``.until`` as one parsed from iCalendar, consistent with #1987/#1986's
    fix to ``from_xcal``'s UNTIL handling."""
    xml = list2xml(
        ["recur", ["freq", "DAILY"], ["until", ["date-time", "2026-12-31T23:59:59Z"]]]
    )
    recur = vRecur.from_xcal(xml)
    assert recur.until == datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    assert recur.to_ical() == b"FREQ=DAILY;UNTIL=20261231T235959Z"


def test_until_returns_a_raw_date_when_parsed_from_xcal():
    xml = list2xml(["recur", ["freq", "DAILY"], ["until", ["date", "2026-12-31"]]])
    recur = vRecur.from_xcal(xml)
    assert recur.until == date(2026, 12, 31)
    assert recur.to_ical() == b"FREQ=DAILY;UNTIL=20261231"
