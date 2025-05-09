"""Events differ although their times are equal."""
from datetime import date, datetime, timedelta, timezone

import pytest

from icalendar import Event, Journal, vDate, vDatetime, vDDDLists, vDDDTypes

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore PGH003



def to_dt(a:date) -> date:
    return a

def to_event(a):
    e = Event()
    e.start = a
    e.end = a + timedelta(days=1)
    e.add("RECURRENCE-ID", a - timedelta(days=1))
    return e

def to_journal(a):
    """return a journal for testing"""
    j = Journal()
    j.start = a
    j.end = a + timedelta(days=1)
    j.add("RECURRENCE-ID", a - timedelta(days=1))
    return j

def to_vDD(a):
    """Return a value type."""
    if isinstance(a, datetime):
        return vDatetime(a)
    return vDate(a)


def to_vDDDTypes(a):
    return vDDDTypes(a)

def to_vDDDLists(a):
    return vDDDLists([a])

equal_dts = pytest.mark.parametrize(
    ("d1", "d2"),
    [
        (date(1998, 10, 1), date(1998, 10, 1)),
        (datetime(2023, 12, 31), datetime(2023, 12, 31)),
        (datetime(2023, 12, 31, tzinfo=timezone.utc), datetime(2023, 12, 31, tzinfo=ZoneInfo("UTC"))),
        (datetime(2023, 12, 31, tzinfo=ZoneInfo("UTC")), datetime(2023, 12, 31, tzinfo=ZoneInfo("UTC"))),
        (datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC")), datetime(2025, 12, 31, tzinfo=ZoneInfo("GMT+0"))),
        (datetime(2025, 12, 31, 12, tzinfo=ZoneInfo("Europe/Zurich")), datetime(2025, 12, 31, 11, tzinfo=ZoneInfo("UTC"))),
    ],
)

@equal_dts
@pytest.mark.parametrize("transform", [
    to_dt, to_event, to_journal, to_vDD, to_vDDDTypes, to_vDDDLists])
def test_equality_of_equal_datetimes(d1, d2, transform):
    """Check that the values are equal."""
    a = transform(d1)
    b = transform(d2)
    assert_eq(a, b)

def assert_eq(a, b):
    """Check all equality tests."""
    assert  a == b, f"1 equal: {a} == {b}"
    assert  b == a, f"2 equal reversed: {b} == {a}"
    assert not a != b, f"3 not equal: {a} != {b}"  # noqa: SIM202
    assert not b != a, f"4 not equal reversed: {b} != {a}"  # noqa: SIM202
    assert bool(a) == bool(b), f"5 equal bool: {bool(a)} == {bool(b)}"


dts = [to_dt, to_vDD, to_vDDDTypes, to_vDDDLists]

@pytest.mark.parametrize("transform1", dts)
@pytest.mark.parametrize("transform2", dts)
@equal_dts
def test_property_times_for_date_and_datetime(d1, d2, transform1, transform2):
    """Check the equality of the date and date implementations."""
    a = transform1(d1)
    b = transform2(d2)
    assert_eq(a, b)


def test_datetime_is_in_list_representation():
    dt = datetime(2023, 12, 31)
    assert str(dt) in str(vDDDLists([dt]))
    