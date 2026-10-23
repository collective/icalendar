import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur, vSkip


def test_skip_returns_none_when_absent():
    """SKIP is not set at all — OMIT is the default value the rule then uses,
    but the accessor reports the missing part as None, like count."""
    assert vRecur.from_ical("FREQ=DAILY").skip is None


def test_skip_returns_the_value_as_a_vskip():
    assert vRecur.from_ical("FREQ=DAILY;SKIP=FORWARD").skip is vSkip.FORWARD


def test_skip_reads_each_of_the_three_rfc_7529_values():
    for name in (vSkip.OMIT, vSkip.FORWARD, vSkip.BACKWARD):
        assert vRecur.from_ical(f"FREQ=DAILY;SKIP={name.value}").skip is name


def test_skip_returns_first_value_when_multiple_are_present():
    """If multiple values are given, the first one is returned."""
    recur = vRecur(FREQ=["DAILY"], SKIP=[vSkip.FORWARD, vSkip.BACKWARD])
    assert recur.skip is vSkip.FORWARD


def test_skip_returns_none_when_value_is_an_empty_list():
    """If an empty list is in there, None is returned."""
    recur = vRecur(FREQ=["DAILY"], SKIP=[])
    assert recur.skip is None


def test_setting_skip_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.skip = vSkip.BACKWARD
    assert recur.skip is vSkip.BACKWARD
    assert recur.to_ical() == b"FREQ=DAILY;SKIP=BACKWARD"


def test_setting_skip_by_name_stores_the_value():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.skip = "FORWARD"
    assert recur.skip is vSkip.FORWARD
    assert recur.to_ical() == b"FREQ=DAILY;SKIP=FORWARD"


def test_setting_skip_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;SKIP=FORWARD")
    recur.skip = None
    assert recur.skip is None
    assert "SKIP" not in recur


def test_deleting_skip_removes_the_value():
    recur = vRecur.from_ical("FREQ=DAILY;SKIP=FORWARD")
    del recur.skip
    assert recur.skip is None
    assert "SKIP" not in recur


def test_deleting_skip_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.skip  # should not raise
    assert recur.skip is None


def test_setting_skip_to_an_unknown_name_raises_invalid_calendar():
    """The parser rejects an unknown SKIP before the accessor is ever reached;
    the setter reports the same boundary for names assigned through it."""
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.skip = "FORWARDS"


def test_setting_skip_is_case_sensitive():
    """RFC 7529 defines SKIP as upper-case tokens and vSkip (an Enum) accepts
    only those; from_ical rejects lowercase the same way, so the setter is
    consistent with the parser rather than silently normalizing."""
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar):
        recur.skip = "backward"


def test_setting_skip_to_a_wrong_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.skip = 5


@pytest.mark.parametrize("stored", ["XX", "", ["XX"]])
def test_directly_assigned_unreadable_skip_raises_invalid_calendar(stored):
    """The only route to an unreadable SKIP is assigning it directly, past
    the parser. Reading it reports InvalidCalendar rather than letting a bare
    ValueError escape."""
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["SKIP"] = stored
    with pytest.raises(InvalidCalendar, match="SKIP must be OMIT, FORWARD or BACKWARD"):
        recur.skip


def test_skip_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;SKIP=BACKWARD")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.skip is vSkip.BACKWARD


def test_skip_parsed_recurs_with_and_without_it_compare_unequal():
    assert vRecur.from_ical("FREQ=DAILY;SKIP=BACKWARD") != vRecur.from_ical(
        "FREQ=DAILY"
    )
