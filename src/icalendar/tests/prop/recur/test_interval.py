"""Tests for the vRecur.interval accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vInt


def test_get_interval_from_ical():
    assert vRecur.from_ical("FREQ=DAILY;INTERVAL=2").interval == 2


def test_get_interval_missing_is_default():
    assert vRecur.from_ical("FREQ=DAILY").interval == 1


def test_get_interval_empty_list_is_default():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = []
    assert recur.interval == 1


def test_get_interval_returns_first_of_multiple():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = [vInt(3), vInt(9)]
    assert recur.interval == 3


def test_set_interval():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.interval = 4
    assert recur.interval == 4
    assert b"INTERVAL=4" in recur.to_ical()


def test_set_interval_none_deletes():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=2")
    recur.interval = None
    assert recur.interval == 1
    assert "INTERVAL" not in recur


def test_del_interval():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=2")
    del recur.interval
    assert recur.interval == 1
    assert "INTERVAL" not in recur


def test_del_interval_when_absent():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.interval
    assert recur.interval == 1


def test_set_rejects_bool():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.interval = True


def test_set_rejects_non_int():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.interval = "2"


def test_set_rejects_zero_and_negative():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.interval = 0
    with pytest.raises(InvalidCalendar):
        recur.interval = -1


def test_get_invalid_stored_values_return_default():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = [vInt(0)]
    assert recur.interval == 1
    recur["INTERVAL"] = [vInt(-3)]
    assert recur.interval == 1
    recur["INTERVAL"] = ["abc"]
    assert recur.interval == 1
    recur["INTERVAL"] = [True]
    assert recur.interval == 1


def test_get_skips_invalid_and_returns_first_valid():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = ["abc", vInt(0), vInt(4)]
    assert recur.interval == 4


def test_round_trip():
    original = vRecur.from_ical("FREQ=MONTHLY;INTERVAL=3")
    parsed = vRecur.from_ical(original.to_ical().decode())
    assert parsed.interval == 3
