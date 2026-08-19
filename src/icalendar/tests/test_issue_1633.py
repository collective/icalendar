"""Periods written with dates are read as midnight datetimes.

RFC 5545, section 3.3.9, builds a period from datetimes only. A period
written with dates used to parse without error and then raise an
``AttributeError`` from ``to_ical()``.

See https://github.com/collective/icalendar/issues/1633
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from icalendar import Event, FreeBusy
from icalendar.prop import vPeriod

UTC_MIDNIGHT = datetime(1997, 1, 1, tzinfo=timezone.utc)


def test_calendar_from_the_issue_round_trips(calendars):
    """The calendar serializes the dates as datetimes at midnight instead of raising."""
    calendar = calendars.issue_1633_rdate_with_dates
    assert b"RDATE;VALUE=PERIOD:19970101T000000/19970102T000000" in calendar.to_ical()


def test_no_error_is_recorded(calendars):
    """The value is understood, so the event is not marked as broken."""
    event = calendars.issue_1633_rdate_with_dates.walk("VEVENT")[0]
    assert event.errors == []


@pytest.mark.parametrize(
    ("ical", "expected"),
    [
        ("19970101/19970102", (datetime(1997, 1, 1), datetime(1997, 1, 2))),
        ("19970101/P1D", (datetime(1997, 1, 1), timedelta(days=1))),
        (
            "19970101T180000/19970102",
            (datetime(1997, 1, 1, 18), datetime(1997, 1, 2)),
        ),
    ],
)
def test_from_ical_converts_dates(ical, expected):
    """Parsing returns datetimes, so the value matches what is written out."""
    assert vPeriod.from_ical(ical) == expected


@pytest.mark.parametrize(
    ("ical", "expected"),
    [
        ("19970101/19970102", b"19970101T000000/19970102T000000"),
        ("19970101/P1D", b"19970101T000000/P1D"),
        ("19970101T180000/19970102", b"19970101T180000/19970102T000000"),
        ("19970101T180000Z/19970102T070000Z", b"19970101T180000Z/19970102T070000Z"),
        ("19970101T180000Z/PT5H30M", b"19970101T180000Z/PT5H30M"),
    ],
)
def test_to_ical(ical, expected):
    """Date-only halves are written out as datetimes, valid values are untouched."""
    assert vPeriod(vPeriod.from_ical(ical)).to_ical() == expected


@pytest.mark.parametrize(
    ("ical", "expected"),
    [
        ("19970101/19970102T070000Z", b"19970101T000000Z/19970102T070000Z"),
        ("19970101T180000Z/19970102", b"19970101T180000Z/19970102T000000Z"),
    ],
)
def test_a_converted_date_takes_the_timezone_of_the_other_half(tzp, ical, expected):
    """A date next to an aware datetime cannot stay naive.

    The two halves could not be subtracted to compute the duration.
    """
    period = vPeriod.from_ical(ical)
    assert period[0].tzinfo is not None
    assert period[1].tzinfo is not None
    assert vPeriod(period).to_ical() == expected


def test_a_borrowed_timezone_uses_the_offset_of_its_own_date(tzp):
    """The end is in summer, so it takes the summer offset of the timezone.

    A pytz timezone carries one offset per period of its history, so the
    offset of the start cannot simply be copied over.
    """
    start = tzp.localize(datetime(1997, 7, 1, 12), "America/New_York")
    _start, end = vPeriod((start, date(1997, 7, 2))).dt
    assert end.utcoffset() == timedelta(hours=-4)


def test_a_converted_start_borrows_a_named_timezone(tzp):
    """The start date takes the summer offset of the other half's zone."""
    end = tzp.localize(datetime(1997, 7, 2, 12), "America/New_York")
    start, _end = vPeriod((date(1997, 7, 1), end)).dt
    assert start.utcoffset() == timedelta(hours=-4)


def test_a_timezone_that_the_provider_does_not_use(tzp):
    """The timezone comes from the value, not from the active provider."""
    period = vPeriod((date(1997, 1, 1), datetime(1997, 1, 2, 7, tzinfo=timezone.utc)))
    assert period.to_ical() == b"19970101T000000Z/19970102T070000Z"


def test_the_start_keeps_its_moment_in_time(tzp):
    """Converting the start does not move it to another instant."""
    start, _end = vPeriod.from_ical("19970101/19970102T070000Z")
    assert start == UTC_MIDNIGHT


def test_freebusy_round_trips(calendars):
    """FREEBUSY is a period too, in a component that does not ignore errors."""
    calendar = calendars.issue_1633_freebusy_with_dates
    assert b"FREEBUSY:19970101T000000/19970102T000000" in calendar.to_ical()


@pytest.mark.parametrize(
    ("period", "expected"),
    [
        ((date(1997, 1, 1), date(1997, 1, 2)), b"19970101T000000/19970102T000000"),
        ((date(1997, 1, 1), timedelta(days=1)), b"19970101T000000/P1D"),
        (
            (date(1997, 1, 1), datetime(1997, 1, 2, 7)),
            b"19970101T000000/19970102T070000",
        ),
    ],
)
def test_a_period_can_be_built_from_dates(period, expected):
    """Passing a date is a mistake that is understood rather than rejected."""
    assert vPeriod(period).to_ical() == expected


def test_dates_added_to_a_component():
    """``add`` builds the period through vDDDLists."""
    event = Event()
    event.add("RDATE", [(date(1997, 1, 1), date(1997, 1, 2))])
    assert b"19970101T000000/19970102T000000" in event.to_ical()


def test_dates_added_to_a_freebusy():
    """``add`` builds the period through vPeriod itself."""
    freebusy = FreeBusy()
    freebusy.add("FREEBUSY", [(date(1997, 1, 1), date(1997, 1, 2))])
    assert b"19970101T000000/19970102T000000" in freebusy.to_ical()


def test_a_comma_separated_period_list_round_trips():
    """A date-only period next to a normal one survives the list split."""
    event = Event()
    event.add(
        "RDATE",
        [
            (date(1997, 1, 1), date(1997, 1, 2)),
            (datetime(1997, 7, 5, 12), datetime(1997, 7, 6)),
        ],
    )
    ical = event.to_ical()
    assert b"19970101T000000/19970102T000000,19970705T120000/19970706T000000" in ical
    parsed = Event.from_ical(ical)
    assert parsed["RDATE"].dts[0].dt[0] == datetime(1997, 1, 1)


def test_the_duration_is_computed_from_the_converted_values():
    """The duration is available, where it used to be impossible to compute."""
    period = vPeriod((date(1997, 1, 1), date(1997, 1, 3)))
    assert period.duration == timedelta(days=2)


def test_a_period_with_a_tzid_is_unchanged(tzp, calendars):
    """This form already converted before the fix and still does."""
    calendar = calendars.issue_1633_rdate_with_dates_and_tzid
    event = calendar.walk("VEVENT")[0]
    start, end = event["RDATE"].dts[0].dt
    assert start.replace(tzinfo=None) == datetime(1997, 1, 1)
    assert end.replace(tzinfo=None) == datetime(1997, 1, 2)
    assert start.tzinfo is not None
    assert (
        b"RDATE;TZID=America/New_York;VALUE=PERIOD:"
        b"19970101T000000/19970102T000000" in calendar.to_ical()
    )


def test_an_invalid_period_is_still_invalid():
    """Conversion does not make broken values parse."""
    with pytest.raises(ValueError, match="Expected period format"):
        vPeriod.from_ical("19970101/not-a-date")


def test_an_end_date_before_the_start_is_rejected():
    """Midnight is the whole of the reading, the end is not stretched to the day.

    ``19970102T120000Z/19970102`` asks for an end that midnight puts before
    the start, so the period is invalid. Reading the end as the end of that
    day would invent a duration the calendar never stated.
    """
    with pytest.raises(ValueError, match="Start time is greater than end time"):
        vPeriod(vPeriod.from_ical("19970102T120000Z/19970102"))
