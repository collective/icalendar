import pytest

from icalendar.prop import vRecur


def test_count_returns_none_when_absent():
    """COUNT is not set at all."""
    assert vRecur.from_ical("FREQ=DAILY").count is None


def test_count_returns_the_value():
    assert vRecur.from_ical("FREQ=DAILY;COUNT=10").count == 10


def test_count_of_zero_is_returned_as_zero_not_none():
    """RFC 5545's grammar for COUNT is ``1*DIGIT``, so 0 is a valid value
    and must not be treated the same as COUNT being absent."""
    assert vRecur.from_ical("FREQ=DAILY;COUNT=0").count == 0


def test_count_returns_first_value_when_multiple_are_present():
    """If multiple values are given, the first one is returned."""
    recur = vRecur(FREQ=["DAILY"], COUNT=[10, 20])
    assert recur.count == 10


def test_count_returns_none_when_value_is_an_empty_list():
    """If an empty list is in there, None is returned."""
    recur = vRecur(FREQ=["DAILY"], COUNT=[])
    assert recur.count is None


def test_setting_count_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.count = 5
    assert recur.count == 5
    assert recur.to_ical() == b"FREQ=DAILY;COUNT=5"


def test_setting_count_to_zero_stores_zero():
    """0 is a valid COUNT per the RFC 5545 grammar (``1*DIGIT``); it is not
    special-cased as equivalent to deleting the value."""
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.count = 0
    assert recur.count == 0
    assert "COUNT" in recur
    assert recur.to_ical() == b"FREQ=DAILY;COUNT=0"


def test_setting_count_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    recur.count = None
    assert recur.count is None
    assert "COUNT" not in recur


def test_deleting_count_removes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    del recur.count
    assert recur.count is None
    assert "COUNT" not in recur


def test_deleting_count_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.count  # should not raise
    assert recur.count is None


def test_setting_count_to_non_int_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.count = "10"


def test_setting_count_to_bool_raises_type_error():
    """bool is technically an int subclass but not a valid COUNT."""
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.count = True


def test_setting_count_to_negative_raises_value_error():
    """RFC 5545's grammar for COUNT is ``1*DIGIT`` -- unsigned digits only,
    so a negative value is never valid, even though 0 is."""
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(ValueError):
        recur.count = -1


def test_count_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.count == 10


def test_count_of_zero_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=0")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.count == 0
