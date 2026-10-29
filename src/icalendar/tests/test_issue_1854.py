"""Regression tests for issue #1854."""

import pytest

from icalendar.prop import vRecur


def test_byweekday_is_normalized_to_byday_in_ical():
    """The non-standard iCalendar alias is parsed and serialized as BYDAY."""
    recur = vRecur.from_ical("FREQ=WEEKLY;BYWEEKDAY=TH")

    assert recur == {"FREQ": ["WEEKLY"], "BYDAY": ["TH"]}
    assert recur.to_ical() == b"FREQ=WEEKLY;BYDAY=TH"


def test_byweekday_alias_is_normalized_in_constructor():
    """The dateutil spelling is accepted when constructing a recurrence."""
    recur = vRecur(FREQ="WEEKLY", byweekday="TH")

    assert recur == {"FREQ": ["WEEKLY"], "BYDAY": ["TH"]}
    assert recur.to_ical() == b"FREQ=WEEKLY;BYDAY=TH"


def test_byweekday_and_byday_cannot_both_be_specified():
    """Conflicting spellings must not silently discard either value."""
    with pytest.raises(
        ValueError, match="BYDAY and BYWEEKDAY cannot both be specified"
    ):
        vRecur(BYDAY="MO", BYWEEKDAY="TH")


def test_byweekday_is_normalized_in_jcal():
    """The dateutil alias is parsed and emitted as jCal ``byday``."""
    recur = vRecur.from_jcal(
        ["rrule", {}, "recur", {"byweekday": ["MO"], "freq": "WEEKLY"}]
    )

    assert recur == {"FREQ": "WEEKLY", "BYDAY": ["MO"]}
    assert recur.to_jcal("rrule") == [
        "rrule",
        {},
        "recur",
        {"freq": "WEEKLY", "byday": ["MO"]},
    ]
