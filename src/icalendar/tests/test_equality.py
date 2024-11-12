"""Test the equality and inequality of components."""

import contextlib
import copy

try:
    from pytz import UnknownTimeZoneError
except ImportError:
    class UnknownTimeZoneError(Exception):
        pass
from datetime import date, datetime, time, timedelta

import pytest

from icalendar.prop import (
    vBinary,
    vBoolean,
    vCategory,
    vDate,
    vDatetime,
    vDDDLists,
    vDDDTypes,
    vDuration,
    vGeo,
    vPeriod,
    vText,
    vTime,
)


def assert_equal(actual_value, expected_value):
    """Make sure both values are equal"""
    assert actual_value == expected_value
    assert expected_value == actual_value


def assert_not_equal(actual_value, expected_value):
    """Make sure both values are not equal"""
    assert actual_value != expected_value
    assert expected_value != actual_value


def test_parsed_calendars_are_equal_if_parsed_again(ics_file, tzp):
    """Ensure that a calendar equals the same calendar.

    ics -> calendar -> ics -> same calendar
    """
    copy_of_calendar = ics_file.__class__.from_ical(ics_file.to_ical())
    assert_equal(copy_of_calendar, ics_file)


def test_parsed_calendars_are_equal_if_from_same_source(ics_file, tzp):
    """Ensure that a calendar equals the same calendar.

    ics -> calendar
    ics -> same calendar
    """
    cal1 = ics_file.__class__.from_ical(ics_file.raw_ics)
    cal2 = ics_file.__class__.from_ical(ics_file.raw_ics)
    assert_equal(cal1, cal2)


def test_copies_are_equal(ics_file, tzp):
    """Ensure that copies are equal."""
    copy1 = ics_file.copy()
    copy1.subcomponents = ics_file.subcomponents
    copy2 = ics_file.copy()
    copy2.subcomponents = ics_file.subcomponents[:]
    assert_equal(copy1, copy2)
    assert_equal(copy1, ics_file)
    assert_equal(copy2, ics_file)


def test_copy_does_not_copy_subcomponents(calendars, tzp):
    """If we copy the subcomponents, assumptions around copies will be broken."""
    assert calendars.timezoned.subcomponents
    assert not calendars.timezoned.copy().subcomponents


def test_deep_copies_are_equal(ics_file, tzp):
    """Ensure that deep copies are equal.

    Ignore errors when a custom time zone is used.
    This is still covered by the parsing test.
    """
    if ics_file.source_file == "issue_722_timezone_transition_ambiguity.ics" and tzp.uses_zoneinfo():
        pytest.skip("This test fails for now.")
    with contextlib.suppress(UnknownTimeZoneError):
        assert_equal(copy.deepcopy(ics_file), copy.deepcopy(ics_file))
    with contextlib.suppress(UnknownTimeZoneError):
        assert_equal(copy.deepcopy(ics_file), ics_file)


def test_vGeo():
    """Check the equality of vGeo."""
    assert_equal(vGeo(("100", "12.33")), vGeo(("100.00", "12.330")))
    assert_not_equal(vGeo(("100", "12.331")), vGeo(("100.00", "12.330")))
    assert_not_equal(vGeo(("10", "12.33")), vGeo(("100.00", "12.330")))


def test_vBinary():
    assert_equal(vBinary("asd"), vBinary("asd"))
    assert_not_equal(vBinary("asdf"), vBinary("asd"))


def test_vBoolean():
    assert_equal(vBoolean.from_ical("TRUE"), vBoolean.from_ical("TRUE"))
    assert_equal(vBoolean.from_ical("FALSE"), vBoolean.from_ical("FALSE"))
    assert_not_equal(vBoolean.from_ical("TRUE"), vBoolean.from_ical("FALSE"))


def test_vCategory():
    assert_equal(vCategory("HELLO"), vCategory("HELLO"))
    assert_equal(vCategory(["a", "b"]), vCategory(["a", "b"]))
    assert_not_equal(vCategory(["a", "b"]), vCategory(["a", "b", "c"]))


def test_vText():
    assert_equal(vText("HELLO"), vText("HELLO"))
    assert_not_equal(vText("HELLO1"), vText("HELLO"))


@pytest.mark.parametrize(
    ("vType", "v1", "v2"),
    [
        (vDatetime, datetime(2023, 11, 1, 10, 11), datetime(2023, 11, 1, 10, 10)),
        (vDate, date(2023, 11, 1), date(2023, 10, 31)),
        (vDuration, timedelta(3, 11, 1), timedelta(23, 10, 31)),
        (
            vPeriod,
            (datetime(2023, 11, 1, 10, 11), timedelta(3, 11, 1)),
            (datetime(2023, 11, 1, 10, 11), timedelta(23, 10, 31)),
        ),
        (
            vPeriod,
            (datetime(2023, 11, 1, 10, 1), timedelta(3, 11, 1)),
            (datetime(2023, 11, 1, 10, 11), timedelta(3, 11, 1)),
        ),
        (
            vPeriod,
            (datetime(2023, 11, 1, 10, 1), datetime(2023, 11, 1, 10, 3)),
            (datetime(2023, 11, 1, 10, 1), datetime(2023, 11, 1, 10, 2)),
        ),
        (vTime, time(10, 10, 10), time(10, 10, 11)),
    ],
)
@pytest.mark.parametrize("eq", ["==", "!="])
@pytest.mark.parametrize("cls1", [0, 1])
@pytest.mark.parametrize("cls2", [0, 1])
@pytest.mark.parametrize("hash", [lambda x: x, hash])
def test_vDDDTypes_and_others(vType, v1, v2, cls1, cls2, eq, hash):
    """Check equality and inequality."""
    t1 = (vType, vDDDTypes)[cls1]
    t2 = (vType, vDDDTypes)[cls2]
    if eq == "==":
        assert hash(v1) == hash(v1)
        assert hash(t1(v1)) == hash(t2(v1))
        assert hash(t1(v1)) == hash(t2(v1))
    else:
        assert hash(v1) != hash(v2)
        assert hash(t1(v1)) != hash(t2(v2))


def test_repr_vDDDTypes():
    assert "vDDDTypes" in repr(vDDDTypes(timedelta(3, 11, 1)))


vDDDLists_examples = [  # noqa: N816
    vDDDLists([]),
    vDDDLists([datetime(2023, 11, 1, 10, 1)]),
    vDDDLists([datetime(2023, 11, 1, 10, 1), date(2023, 11, 1)]),
]


@pytest.mark.parametrize("l1", vDDDLists_examples)
@pytest.mark.parametrize("l2", vDDDLists_examples)
def test_vDDDLists(l1, l2):
    """Check the equality functions of vDDDLists."""
    equal = l1 is l2
    l2 = copy.deepcopy(l2)
    assert equal == (l1 == l2)
    assert equal != (l1 != l2)
