"""This tests the RDATE property."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pprint import pprint
from typing import TYPE_CHECKING

import pytest

from icalendar import vDDDLists, vDDDTypes
from icalendar.cal.event import Event
from icalendar.cal.journal import Journal
from icalendar.cal.timezone import TimezoneDaylight, TimezoneStandard
from icalendar.cal.todo import Todo

if TYPE_CHECKING:
    from icalendar.cal.calendar import (
        Calendar,
    )

C_RDATE = Event | Todo | Journal | TimezoneDaylight | TimezoneStandard


@pytest.fixture(params=[Event, Todo, Journal, TimezoneDaylight, TimezoneStandard])
def c_rdate(request) -> C_RDATE:
    """Return a component that uses RDATE."""
    return request.param()


@pytest.fixture(
    params=[
        lambda _tzp: date(2019, 10, 11),
        lambda _tzp: datetime(2000, 1, 13, 12, 1),
        lambda tzp: tzp.localize_utc(datetime(2031, 12, 1, 23, 59)),
        lambda tzp: tzp.localize(datetime(1984, 1, 13, 13, 1), "Europe/Athens"),
        lambda _tzp: ((datetime(2000, 1, 13, 12, 1), datetime(2000, 1, 13, 12, 2))),
        lambda tzp: (
            (
                tzp.localize_utc(datetime(2001, 1, 13, 12, 1)),
                tzp.localize_utc(datetime(2001, 1, 13, 12, 2)),
            )
        ),
    ]
)
def rdate(request, tzp):
    """Possible values for an rdate."""
    return request.param(tzp)


def test_no_rdates_by_default(c_rdate):
    """We expect no rdate by default."""
    assert c_rdate.rdates == []


def test_set_and_retrieve_rdate(rdate, c_rdate):
    """Set the attribute and get the value."""
    c_rdate.add("RDATE", [rdate])
    result = [rdate if isinstance(rdate, tuple) else (rdate, None)]
    assert c_rdate.rdates == result


def test_get_example_0(calendars):
    """Test an example rdate."""
    cal: Calendar = calendars.rfc_5545_RDATE_example
    event = cal.events[0]
    assert event.rdates == [(datetime(1997, 7, 14, 12, 30), None)]


def test_get_example_1(calendars, tzp):
    """Test an example rdate."""
    cal: Calendar = calendars.rfc_5545_RDATE_example
    event = cal.events[1]
    assert event.rdates == [(tzp.localize_utc(datetime(1997, 7, 14, 12, 30)), None)]


def test_get_example_2(calendars, tzp):
    """Test an example rdate."""
    cal: Calendar = calendars.rfc_5545_RDATE_example
    event = cal.events[2]
    assert event.rdates == [
        (tzp.localize(datetime(1997, 7, 14, 8, 30), "America/New_York"), None)
    ]


def test_get_example_3(calendars, tzp):
    """Test an example rdate."""
    cal: Calendar = calendars.rfc_5545_RDATE_example
    event = cal.events[3]
    rdates_3 = [
        (
            tzp.localize_utc(datetime(1996, 4, 3, 2)),
            tzp.localize_utc(datetime(1996, 4, 3, 4)),
        ),
        (
            tzp.localize_utc(datetime(1996, 4, 4, 1)),
            tzp.localize_utc(datetime(1996, 4, 4, 4)),
        ),
    ]
    pprint(event.rdates)
    pprint(rdates_3)
    assert event.rdates == rdates_3


def d(i: int) -> tuple[date, None]:
    s = str(i)
    return (date(int(s[:4]), int(s[4:6].lstrip("0")), int(s[6:].lstrip("0"))), None)


RDATES_4 = list(
    map(
        d,
        (
            19970101,
            19970120,
            19970217,
            19970421,
            19970526,
            19970704,
            19970901,
            19971014,
            19971128,
            19971129,
            19971225,
        ),
    )
)


def test_get_example_4(calendars, tzp):
    """Test an example rdate."""
    cal: Calendar = calendars.rfc_5545_RDATE_example
    event = cal.events[4]
    pprint(event.rdates)
    pprint(RDATES_4)
    assert event.rdates == RDATES_4


# Equivalent ways to write a single date that all mean that one date after #1439:
# the ``(dt, None)`` rdates form, that form wrapped in a list as ``.rdates``
# returns it, and the same pair as a plain list ``[dt, None]``.
SINGLE_DATE = datetime(2025, 4, 28, 16, 5)
SINGLE_DATE_FORMS = [(SINGLE_DATE, None), [(SINGLE_DATE, None)], [SINGLE_DATE, None]]


@pytest.mark.parametrize("value", SINGLE_DATE_FORMS)
def test_add_rdate_with_none_end_sets_a_single_date(c_rdate, value):
    """``(dt, None)`` is the rdates form of a single date, so adding it sets that
    one date instead of raising (#1439)."""
    c_rdate.add("RDATE", value)
    assert c_rdate.rdates == [(SINGLE_DATE, None)]


@pytest.mark.parametrize("value", SINGLE_DATE_FORMS)
def test_add_rdate_with_none_end_serializes_like_the_bare_date(c_rdate, value):
    """Adding ``(dt, None)`` serializes identically to adding the bare ``dt`` — the
    bug surfaced only at ``to_ical`` time (#1439)."""
    bare = c_rdate.__class__()
    bare.add("RDATE", SINGLE_DATE)
    c_rdate.add("RDATE", value)
    assert c_rdate.to_ical() == bare.to_ical()


def test_rdates_output_can_be_added_back(c_rdate):
    """The value returned by ``.rdates`` can be fed straight back into ``add`` (#1439)."""
    c_rdate.add("RDATE", SINGLE_DATE)
    restored = c_rdate.__class__()
    restored.add("RDATE", c_rdate.rdates)
    assert restored.rdates == c_rdate.rdates


def test_rdates_output_added_back_serializes_identically(c_rdate):
    """Re-adding ``.rdates`` also round-trips through serialization (#1439)."""
    c_rdate.add("RDATE", SINGLE_DATE)
    restored = c_rdate.__class__()
    restored.add("RDATE", c_rdate.rdates)
    assert restored.to_ical() == c_rdate.to_ical()


def test_add_rdate_two_datetimes_stays_two_values(c_rdate):
    """A ``(dt1, dt2)`` tuple keeps its meaning of two separate dates, so only the
    ``None`` second-element case is treated as a single date (#1439)."""
    second = datetime(2025, 4, 29, 16, 5)
    c_rdate.add("RDATE", (SINGLE_DATE, second))
    assert c_rdate.rdates == [(SINGLE_DATE, None), (second, None)]


@pytest.mark.parametrize("value", [(SINGLE_DATE, None), [SINGLE_DATE, None]])
def test_vdddtypes_treats_none_end_pair_as_a_bare_date(value):
    """``vDDDTypes`` builds the date itself rather than an invalid period from a
    ``(dt, None)`` pair, given as a tuple or a list — the lower-level half of #1439."""
    assert vDDDTypes(value).dt == SINGLE_DATE


@pytest.mark.parametrize("value", [(SINGLE_DATE, None), [SINGLE_DATE, None]])
def test_vdddlists_treats_none_end_pair_as_a_single_date(value):
    """``vDDDLists`` treats a ``(dt, None)`` pair, tuple or list, as one date instead
    of iterating it into two values — the other half of #1439."""
    assert vDDDLists(value).to_ical() == vDDDLists([SINGLE_DATE]).to_ical()


def test_set_all_rdate_value_types_then_round_trip(c_rdate, tzp):
    """Setting RDATE with one of every accepted value type works, and feeding the
    resulting ``.rdates`` straight back in leaves value, length and content
    unchanged (#1439)."""
    utc_dt = tzp.localize_utc(datetime(2031, 12, 1, 23, 59))
    zoned_dt = tzp.localize(datetime(1984, 1, 13, 13, 1), "Europe/Athens")
    period_start, period_end = (
        datetime(2000, 1, 13, 12, 1),
        datetime(2000, 1, 13, 12, 2),
    )
    dur_start = datetime(2032, 6, 1, 9, 0)
    # Each accepted value paired with the (start, end) ``.rdates`` should yield.
    cases = [
        (date(2019, 10, 11), (date(2019, 10, 11), None)),  # a bare date
        (datetime(2000, 1, 13, 12, 1), (datetime(2000, 1, 13, 12, 1), None)),  # naive
        (utc_dt, (utc_dt, None)),  # a UTC datetime
        (zoned_dt, (zoned_dt, None)),  # a zoned datetime
        ((period_start, period_end), (period_start, period_end)),  # a period
        (
            (dur_start, timedelta(hours=2)),
            (dur_start, dur_start + timedelta(hours=2)),
        ),  # period as (start, duration)
        ((SINGLE_DATE, None), (SINGLE_DATE, None)),  # the (dt, None) single-date form
    ]

    # (1) Setting every value type at once produces the expected rdates.
    c_rdate.add("RDATE", [value for value, _ in cases])
    assert c_rdate.rdates == [result for _, result in cases]

    # (2) Setting rdates to its own output round-trips without changing anything.
    restored = c_rdate.__class__()
    restored.add("RDATE", c_rdate.rdates[:])
    assert restored.rdates == c_rdate.rdates


def test_set_rdates_via_property(c_rdate):
    """``.rdates`` is settable and replaces any existing RDATE (#1442)."""
    c_rdate.add("RDATE", datetime(2020, 1, 1, 12, 0))
    c_rdate.rdates = [SINGLE_DATE]
    assert c_rdate.rdates == [(SINGLE_DATE, None)]


def test_set_rdates_via_property_all_value_types(c_rdate, tzp):
    """Assigning ``.rdates`` a list with one of every accepted value type sets
    them all through the property setter (#1442, part 1)."""
    utc_dt = tzp.localize_utc(datetime(2031, 12, 1, 23, 59))
    zoned_dt = tzp.localize(datetime(1984, 1, 13, 13, 1), "Europe/Athens")
    period_start, period_end = (
        datetime(2000, 1, 13, 12, 1),
        datetime(2000, 1, 13, 12, 2),
    )
    dur_start = datetime(2032, 6, 1, 9, 0)
    values = [
        date(2019, 10, 11),  # a bare date
        datetime(2000, 1, 13, 12, 1),  # a naive datetime
        utc_dt,  # a UTC datetime
        zoned_dt,  # a zoned datetime
        (period_start, period_end),  # a period
        (dur_start, timedelta(hours=2)),  # a period given as (start, duration)
        (SINGLE_DATE, None),  # the (dt, None) single-date form
    ]
    c_rdate.rdates = values
    assert c_rdate.rdates == [
        (date(2019, 10, 11), None),
        (datetime(2000, 1, 13, 12, 1), None),
        (utc_dt, None),
        (zoned_dt, None),
        (period_start, period_end),
        (dur_start, dur_start + timedelta(hours=2)),
        (SINGLE_DATE, None),
    ]


def test_set_rdates_via_property_its_own_output_round_trips(c_rdate, tzp):
    """Assigning ``.rdates`` its own getter output (``c.rdates = c.rdates[:]``)
    after setting every value type leaves value, length and content unchanged
    (#1442, part 2)."""
    c_rdate.rdates = [
        date(2019, 10, 11),
        datetime(2000, 1, 13, 12, 1),
        tzp.localize_utc(datetime(2031, 12, 1, 23, 59)),
        (datetime(2000, 1, 13, 12, 1), datetime(2000, 1, 13, 12, 2)),
        (SINGLE_DATE, None),
    ]
    before = c_rdate.rdates
    c_rdate.rdates = c_rdate.rdates[:]
    assert c_rdate.rdates == before
    assert len(c_rdate.rdates) == len(before)


def test_set_rdates_round_trips(c_rdate, rdate):
    """Assigning ``.rdates`` its own value leaves it unchanged for every value
    type (#1442)."""
    c_rdate.add("RDATE", [rdate])
    before = c_rdate.rdates
    c_rdate.rdates = before
    assert c_rdate.rdates == before


def test_del_rdates(c_rdate):
    """Deleting ``.rdates`` removes the RDATE property (#1442)."""
    c_rdate.add("RDATE", SINGLE_DATE)
    del c_rdate.rdates
    assert c_rdate.rdates == []
    assert "RDATE" not in c_rdate


@pytest.mark.parametrize("empty", [[], None])
def test_set_rdates_empty_clears(c_rdate, empty):
    """Setting ``.rdates`` to an empty list or ``None`` clears it (#1442)."""
    c_rdate.add("RDATE", SINGLE_DATE)
    c_rdate.rdates = empty
    assert c_rdate.rdates == []
