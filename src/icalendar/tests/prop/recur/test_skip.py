"""Tests for the vRecur.skip accessor (RFC 7529 SKIP)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop.recur.recur import vRecur
from icalendar.prop.recur.skip import vSkip


def test_skip_is_none_when_absent():
    recur = vRecur.from_ical("FREQ=YEARLY")
    assert recur.skip is None


def test_skip_returns_first_of_multiple_values():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["SKIP"] = [vSkip.FORWARD, vSkip.BACKWARD]
    assert recur.skip == vSkip.FORWARD


def test_empty_skip_sequence_returns_none():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["SKIP"] = []
    assert recur.skip is None


def test_parsed_skip_is_vskip():
    recur = vRecur.from_ical("FREQ=YEARLY;SKIP=FORWARD")
    assert recur.skip == "FORWARD"
    assert isinstance(recur.skip, vSkip)
    assert recur.skip is vSkip.FORWARD


@pytest.mark.parametrize("value", ["OMIT", "FORWARD", "BACKWARD", vSkip.OMIT])
def test_setting_skip(value):
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.skip = value
    assert recur.skip == vSkip(value)


def test_setting_skip_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=YEARLY;SKIP=FORWARD")
    recur.skip = None
    assert recur.skip is None
    assert "SKIP" not in recur


def test_deleting_skip_removes_the_value():
    recur = vRecur.from_ical("FREQ=YEARLY;SKIP=BACKWARD")
    del recur.skip
    assert recur.skip is None
    assert "SKIP" not in recur


def test_deleting_skip_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=YEARLY")
    del recur.skip
    assert recur.skip is None


def test_directly_assigned_string_is_returned_as_vskip():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["SKIP"] = "OMIT"
    assert recur.skip == "OMIT"
    assert isinstance(recur.skip, vSkip)


def test_skip_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=YEARLY;SKIP=FORWARD")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.skip == recur.skip
    assert isinstance(roundtripped.skip, vSkip)


def test_setting_skip_matches_parsed_vrecur():
    """Assigning SKIP must produce the same vRecur as parsing it."""
    parsed = vRecur.from_ical("FREQ=YEARLY;SKIP=FORWARD")
    assigned = vRecur.from_ical("FREQ=YEARLY")
    assigned.skip = "FORWARD"
    assert assigned == parsed
    assert assigned["SKIP"] == parsed["SKIP"]
    assert isinstance(assigned["SKIP"], list)
    assert assigned.to_ical() == parsed.to_ical()


def test_setting_skip_to_non_string_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.skip = 1


def test_setting_skip_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.skip = True


def test_setting_skip_to_invalid_value_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(InvalidCalendar, match="SKIP must be OMIT, FORWARD, or BACKWARD"):
        recur.skip = "SIDEWAYS"


@pytest.mark.parametrize("stored", ["SIDEWAYS", "", ["SIDEWAYS"]])
def test_directly_assigned_unreadable_skip_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["SKIP"] = stored
    with pytest.raises(InvalidCalendar, match="SKIP must be OMIT, FORWARD, or BACKWARD"):
        recur.skip
