"""Tests for the vRecur.interval accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vPositiveInt


def test_interval_returns_none_when_absent():
    assert vRecur.from_ical("FREQ=DAILY").interval is None


def test_interval_returns_the_value():
    assert vRecur.from_ical("FREQ=DAILY;INTERVAL=2").interval == 2


def test_interval_returns_first_value_when_multiple_are_present():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[2, 3])
    assert recur.interval == 2


def test_interval_returns_none_when_value_is_an_empty_list():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[])
    assert recur.interval is None


def test_setting_interval_stores_a_registered_positive_int():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.interval = 3

    assert recur.interval == 3
    assert isinstance(recur["INTERVAL"][0], vPositiveInt)
    assert recur.to_ical() == b"FREQ=DAILY;INTERVAL=3"


def test_setting_interval_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=2")
    recur.interval = None

    assert recur.interval is None
    assert "INTERVAL" not in recur


def test_setting_interval_to_none_removes_all_multiple_values():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[2, 3])
    recur.interval = None

    assert recur.interval is None
    assert "INTERVAL" not in recur


def test_deleting_interval_removes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=2")
    del recur.interval

    assert recur.interval is None
    assert "INTERVAL" not in recur


def test_deleting_interval_removes_all_multiple_values():
    recur = vRecur(FREQ=["DAILY"], INTERVAL=[2, 3])
    del recur.interval

    assert recur.interval is None
    assert "INTERVAL" not in recur


def test_deleting_interval_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.interval
    assert recur.interval is None


@pytest.mark.parametrize("value", ["2", 2.0, True])
def test_setting_interval_to_non_int_raises_type_error(value):
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.interval = value


@pytest.mark.parametrize("value", [0, -1])
def test_setting_interval_to_non_positive_value_raises_invalid_calendar(value):
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar, match="INTERVAL must be >= 1"):
        recur.interval = value


@pytest.mark.parametrize("value", ["0", "-1"])
def test_parsing_non_positive_interval_raises_value_error(value):
    with pytest.raises(ValueError):
        vRecur.from_ical(f"FREQ=DAILY;INTERVAL={value}")


def test_directly_assigned_non_positive_interval_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = [-1]
    with pytest.raises(InvalidCalendar, match="INTERVAL must be >= 1"):
        recur.interval


@pytest.mark.parametrize("stored", ["abc", "", ["abc"], True])
def test_directly_assigned_unreadable_interval_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = stored
    with pytest.raises(InvalidCalendar, match="INTERVAL must be"):
        recur.interval


def test_interval_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;INTERVAL=3")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())

    assert roundtripped.interval == 3
    assert isinstance(roundtripped["INTERVAL"][0], vNonNegativeInt)


def test_setting_interval_matches_parsed_vrecur():
    parsed = vRecur.from_ical("FREQ=DAILY;INTERVAL=3")
    assigned = vRecur.from_ical("FREQ=DAILY")
    assigned.interval = 3

    assert assigned == parsed
    assert assigned["INTERVAL"] == parsed["INTERVAL"]
    assert assigned.to_ical() == parsed.to_ical()


@pytest.mark.parametrize("value", ["0", "-1"])
def test_parsing_non_positive_interval_raises_value_error(value):
    with pytest.raises(ValueError):
        vRecur.from_ical(f"FREQ=DAILY;INTERVAL={value}")


def test_directly_assigned_non_positive_interval_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["INTERVAL"] = [-1]
    with pytest.raises(InvalidCalendar, match="INTERVAL must be >= 1"):
        recur.interval
