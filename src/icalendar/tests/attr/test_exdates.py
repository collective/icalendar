"""This tests the exdate property."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from icalendar import (
    Event,
    Journal,
    TimezoneDaylight,
    TimezoneStandard,
    Todo,
)

C_EXDATE = Event | Todo | Journal | TimezoneDaylight | TimezoneStandard


@pytest.fixture(params=[Event, Todo, Journal, TimezoneDaylight, TimezoneStandard])
def c_exdate(request) -> C_EXDATE:
    """Return a component that uses exdate."""
    return request.param()


@pytest.fixture(
    params=[
        lambda _tzp: date(2019, 10, 11),
        lambda _tzp: datetime(2000, 1, 13, 12, 1),
        lambda tzp: tzp.localize_utc(datetime(2031, 12, 1, 23, 59)),
        lambda tzp: tzp.localize(datetime(1984, 1, 13, 13, 1), "Europe/Athens"),
    ]
)
def exdate(request, tzp):
    """Possible values for an exdate."""
    return request.param(tzp)


def test_no_exdates_by_default(c_exdate):
    """We expect no exdate by default."""
    assert c_exdate.exdates == []


def test_set_and_retrieve_exdate(exdate, c_exdate):
    """Set the attribute and get the value."""
    c_exdate.add("exdate", [exdate])
    result = [exdate]
    assert c_exdate.exdates == result


def test_set_and_retrieve_exdates_in_list(exdate, c_exdate):
    """Set the attribute and get the value."""
    c_exdate.add("exdate", [exdate, exdate])
    result = [exdate, exdate]
    assert c_exdate.exdates == result


def test_set_and_retrieve_exdates_twice(exdate, c_exdate):
    """Set the attribute and get the value."""
    c_exdate.add("exdate", [exdate])
    c_exdate.add("exdate", [exdate])
    result = [exdate, exdate]
    assert c_exdate.exdates == result


def test_set_exdates_via_property(exdate, c_exdate):
    """``.exdates`` is settable and replaces any existing EXDATE (#1442)."""
    c_exdate.add("exdate", [datetime(2020, 1, 1, 12, 0)])
    c_exdate.exdates = [exdate]
    assert c_exdate.exdates == [exdate]


def test_set_exdates_round_trips(exdate, c_exdate):
    """Assigning ``.exdates`` its own value leaves it unchanged (#1442)."""
    c_exdate.add("exdate", [exdate])
    before = c_exdate.exdates
    c_exdate.exdates = before
    assert c_exdate.exdates == before


def test_del_exdates(exdate, c_exdate):
    """Deleting ``.exdates`` removes the EXDATE property (#1442)."""
    c_exdate.add("exdate", [exdate])
    del c_exdate.exdates
    assert c_exdate.exdates == []
    assert "EXDATE" not in c_exdate


@pytest.mark.parametrize("empty", [[], None])
def test_set_exdates_empty_clears(exdate, c_exdate, empty):
    """Setting ``.exdates`` to an empty list or ``None`` clears it (#1442)."""
    c_exdate.add("exdate", [exdate])
    c_exdate.exdates = empty
    assert c_exdate.exdates == []
