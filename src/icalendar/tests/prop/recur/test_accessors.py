"""Accessors for vRecur rule parts requested in issue #1851."""

import datetime

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.recur.skip import vSkip


def test_freq_is_required_and_case_normalized():
    assert vRecur.from_ical("FREQ=daily").freq == "DAILY"
    with pytest.raises(InvalidCalendar):
        _ = vRecur().freq
    with pytest.raises(InvalidCalendar):
        del vRecur.from_ical("FREQ=DAILY").freq


def test_freq_invalid_value_raises():
    recur = vRecur(FREQ=["NOTADAY"])
    with pytest.raises(InvalidCalendar):
        _ = recur.freq


def test_until_returns_datetime_and_excludes_count():
    until = vRecur.from_ical("FREQ=DAILY;UNTIL=19971224T000000Z").until
    assert until == datetime.datetime(1997, 12, 24, tzinfo=datetime.timezone.utc)
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=3")
    recur.until = datetime.date(2020, 1, 1)
    assert recur.until == datetime.date(2020, 1, 1)
    assert recur.count is None
    assert "COUNT" not in recur


def test_count_and_until_together_raise_on_get():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=3;UNTIL=19971224T000000Z")
    with pytest.raises(InvalidCalendar):
        _ = recur.count
    with pytest.raises(InvalidCalendar):
        _ = recur.until


def test_setting_count_deletes_until():
    recur = vRecur.from_ical("FREQ=DAILY;UNTIL=19971224T000000Z")
    recur.count = 4
    assert recur.count == 4
    assert recur.until is None


def test_optional_single_parts_round_trip():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    assert recur.interval is None
    assert recur.wkst is None
    assert recur.skip is None
    assert recur.rscale is None
    recur.interval = 2
    recur.wkst = "su"
    recur.skip = "FORWARD"
    recur.rscale = "GREGORIAN"
    assert recur.interval == 2
    assert recur.wkst == "SU"
    assert recur.skip == vSkip.FORWARD
    assert recur.rscale == "GREGORIAN"
    recur.interval = None
    del recur.wkst
    del recur.skip
    del recur.rscale
    assert recur.interval is None
    assert "WKST" not in recur
    assert "SKIP" not in recur
    assert "RSCALE" not in recur


def test_single_part_uses_first_value_and_empty_list_is_missing():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[2, 4])
    assert recur.interval == 2
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[])
    assert recur.interval is None


def test_list_parts_return_all_values_and_empty_tuple():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO,WE;BYHOUR=9")
    assert recur.byday == ("MO", "WE")
    assert recur.byhour == (9,)
    assert recur.bysecond == ()
    recur.byday = None
    assert recur.byday == ()
    assert "BYDAY" not in recur
    recur.byweekday = ["tu", "-1SU"]
    assert recur.byweekday == ("TU", "-1SU")
    recur.byweekday = []
    assert recur.byweekday == ()


def test_list_part_rejects_out_of_range():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.byhour = [24]
    with pytest.raises(InvalidCalendar):
        recur.bymonthday = [0]
    with pytest.raises(InvalidCalendar):
        recur.interval = 0


def test_stored_invalid_list_value_raises_on_get():
    recur = vRecur(FREQ=["DAILY"], BYHOUR=["nope"])
    with pytest.raises(InvalidCalendar):
        _ = recur.byhour
