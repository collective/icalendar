"""Tests for the vRecur.interval accessor."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur


def test_interval_returns_none_when_absent():
    assert vRecur.from_ical("FREQ=DAILY").interval is None


def test_interval_returns_the_value():
    assert vRecur.from_ical("FREQ=DAILY;INTERVAL=2").interval == 2


def test_interval_returns_first_value_when_multiple_are_present():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[2, 4])
    assert recur.interval == 2


def test_interval_returns_none_when_value_is_an_empty_list():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[])
    assert recur.interval is None


def test_setting_interval_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.interval = 3
    assert recur.interval == 3
    assert recur.to_ical() == b"FREQ=DAILY;INTERVAL=3"


def test_setting_interval_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=2")
    recur.interval = None
    assert recur.interval is None
    assert "INTERVAL" not in recur


def test_deleting_interval_removes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=2")
    del recur.interval
    assert recur.interval is None
    assert "INTERVAL" not in recur


def test_deleting_interval_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.interval
    assert recur.interval is None


def test_setting_interval_to_non_int_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.interval = "2"


def test_setting_interval_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.interval = True


def test_setting_interval_less_than_one_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.interval = 0
    with pytest.raises(InvalidCalendar):
        recur.interval = -1


@pytest.mark.parametrize("stored", ["abc", "", 0, -2, ["abc"]])
def test_directly_assigned_invalid_interval_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = stored
    with pytest.raises(InvalidCalendar):
        recur.interval


def test_interval_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=3")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.interval == 3
