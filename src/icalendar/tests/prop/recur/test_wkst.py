"""Tests for the vRecur.wkst accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur, vWeekday


def test_wkst_returns_none_when_absent():
    assert vRecur.from_ical("FREQ=WEEKLY").wkst is None


def test_wkst_returns_the_value():
    wkst = vRecur.from_ical("FREQ=WEEKLY;WKST=SU").wkst
    assert wkst == "SU"
    assert isinstance(wkst, vWeekday)


def test_wkst_returns_first_value_when_multiple_are_present():
    recur = vRecur(FREQ=["WEEKLY"], WKST=[vWeekday("MO"), vWeekday("SU")])
    assert recur.wkst == "MO"


def test_wkst_returns_none_when_value_is_an_empty_list():
    recur = vRecur(FREQ=["WEEKLY"], WKST=[])
    assert recur.wkst is None


def test_setting_wkst_stores_a_vweekday():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.wkst = "SU"
    assert recur.wkst == "SU"
    assert isinstance(recur["WKST"][0], vWeekday)
    assert recur.to_ical() == b"FREQ=WEEKLY;WKST=SU"


def test_setting_wkst_to_vweekday_stores_the_value():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.wkst = vWeekday("FR")
    assert recur.wkst == "FR"


def test_setting_wkst_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=WEEKLY;WKST=SU")
    recur.wkst = None
    assert recur.wkst is None
    assert "WKST" not in recur


def test_deleting_wkst_removes_the_value():
    recur = vRecur.from_ical("FREQ=WEEKLY;WKST=SU")
    del recur.wkst
    assert recur.wkst is None
    assert "WKST" not in recur


def test_deleting_wkst_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    del recur.wkst
    assert recur.wkst is None


def test_directly_assigned_string_is_returned_as_vweekday():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur["WKST"] = "TH"
    assert recur.wkst == "TH"
    assert isinstance(recur.wkst, vWeekday)


def test_wkst_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=WEEKLY;WKST=SU")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.wkst == recur.wkst
    assert isinstance(roundtripped.wkst, vWeekday)


def test_setting_wkst_matches_parsed_vrecur():
    """Assigning WKST must produce the same vRecur as parsing it.

    ``from_ical`` stores ``WKST`` as a one-item list of ``vWeekday``, so
    the setter keeps that representation rather than a bare value.
    """
    parsed = vRecur.from_ical("FREQ=WEEKLY;WKST=SU")
    assigned = vRecur.from_ical("FREQ=WEEKLY")
    assigned.wkst = "SU"
    assert assigned == parsed
    assert assigned["WKST"] == parsed["WKST"]
    assert isinstance(assigned["WKST"], list)
    assert assigned.to_ical() == parsed.to_ical()


def test_setting_wkst_to_non_weekday_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    with pytest.raises(TypeError):
        recur.wkst = 1


def test_setting_wkst_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    with pytest.raises(TypeError):
        recur.wkst = True


def test_setting_wkst_to_invalid_weekday_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    with pytest.raises(InvalidCalendar, match="WKST must be a weekday"):
        recur.wkst = "XX"


@pytest.mark.parametrize("stored", ["XX", "", ["XX"]])
def test_directly_assigned_unreadable_wkst_raises_invalid_calendar(stored):
    """The only route to an unreadable WKST is assigning it directly, past
    the parser. Reading it reports InvalidCalendar rather than letting a
    bare ValueError escape."""
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur["WKST"] = stored
    with pytest.raises(InvalidCalendar, match="WKST must be a weekday"):
        recur.wkst
