"""Test common properties of components."""

from datetime import date, datetime, timedelta

import pytest

from icalendar import Event, FreeBusy, Journal, Todo, vDDDTypes
from icalendar.cal import InvalidCalendar


@pytest.fixture(params=[Event, Todo, Journal, FreeBusy])
def dtstamp_comp(request):
    """a component to test"""
    return request.param()


def test_no_dtstamp(dtstamp_comp):
    """We have None as a value."""
    assert dtstamp_comp.DTSTAMP is None


@pytest.mark.parametrize(
    ("value", "timezone", "expected"),
    [
        (datetime(2024, 10, 11, 23, 1), None, datetime(2024, 10, 11, 23, 1)),
        (datetime(2024, 10, 11, 23, 1), "Europe/Berlin", datetime(2024, 10, 11, 21, 1)),
        (datetime(2024, 10, 11, 22, 1), "UTC", datetime(2024, 10, 11, 22, 1)),
        (date(2024, 10, 10), None, datetime(2024, 10, 10)),
    ]
)
def test_set_value_and_get_it(dtstamp_comp, value, timezone, expected, tzp):
    """Set and get the DTSTAMP value."""
    dtstamp = value if timezone is None else tzp.localize(value, timezone)
    dtstamp_comp.DTSTAMP = dtstamp
    in_utc = tzp.localize_utc(expected)
    get_value = dtstamp_comp.get("DTSTAMP").dt
    assert in_utc == get_value
    assert in_utc == dtstamp_comp.DTSTAMP


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        timedelta()
    ]
)
def test_set_invalid_value(invalid_value, dtstamp_comp):
    """Check handling of invalid values."""
    with pytest.raises(TypeError) as e:
        dtstamp_comp.DTSTAMP = invalid_value
    assert e.value.args[0] == f"DTSTAMP takes a datetime in UTC, not {invalid_value}"


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        vDDDTypes(timedelta())
    ]
)
def test_get_invalid_value(invalid_value, dtstamp_comp):
    """Check handling of invalid values."""
    dtstamp_comp["DTSTAMP"] = invalid_value
    with pytest.raises(InvalidCalendar) as e:
        dtstamp_comp.DTSTAMP  # noqa: B018
    assert e.value.args[0] == f"DTSTAMP must be a datetime in UTC, not {getattr(invalid_value, 'dt', invalid_value)}"


def test_set_twice(dtstamp_comp, tzp):
    """Set the value twice."""
    dtstamp_comp.DTSTAMP = date(2014, 1, 1)
    dtstamp_comp.DTSTAMP = date(2014, 1, 2)
    assert tzp.localize_utc(datetime(2014, 1, 2)) == dtstamp_comp.DTSTAMP
