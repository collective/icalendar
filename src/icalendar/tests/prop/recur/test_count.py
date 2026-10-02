import pytest

from icalendar.error import InvalidCalendar
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


def test_setting_count_to_negative_raises_invalid_calendar():
    """RFC 5545's grammar for COUNT is ``1*DIGIT`` -- unsigned digits only,
    so a negative value is never valid, even though 0 is.

    ``InvalidCalendar`` subclasses ``ValueError``, matching how
    ``icalendar.attr.single_int_property`` reports an out-of-range value.
    """
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.count = -1


def test_non_numeric_count_cannot_be_parsed_at_all():
    """A non-numeric COUNT is rejected while parsing, before the accessor is
    ever reached, so it cannot arrive in a vRecur through from_ical."""
    with pytest.raises(ValueError, match="Expected int, got: abc"):
        vRecur.from_ical("FREQ=DAILY;COUNT=abc")


@pytest.mark.parametrize("stored", ["abc", "", ["abc"]])
def test_directly_assigned_unreadable_count_raises_invalid_calendar(stored):
    """The only route to an unreadable COUNT is assigning it directly, past
    the parser. Reading it reports InvalidCalendar rather than letting a bare
    int() error escape."""
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["COUNT"] = stored
    with pytest.raises(InvalidCalendar, match="COUNT must be an int"):
        recur.count


def test_count_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.count == 10


def test_count_of_zero_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=0")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.count == 0
