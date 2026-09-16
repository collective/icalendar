"""TZP.localize and TZP.localize_utc accept date, datetime and time.

date     -> datetime
datetime -> datetime
time     -> time

See https://github.com/collective/icalendar/issues/1802
"""

from datetime import date, datetime, time

import pytest


# ---------------------------------------------------------------- localize

def test_localize_date_returns_datetime(tzp):
    result = tzp.localize(date(2024, 1, 15), "Europe/Berlin")
    assert isinstance(result, datetime)
    assert result.tzinfo is not None
    assert (result.year, result.month, result.day) == (2024, 1, 15)
    assert (result.hour, result.minute, result.second) == (0, 0, 0)


def test_localize_datetime_returns_datetime(tzp):
    result = tzp.localize(datetime(2024, 1, 15, 10, 30), "Europe/Berlin")
    assert isinstance(result, datetime)
    assert result.tzinfo is not None
    assert (result.hour, result.minute) == (10, 30)


def test_localize_time_returns_time(tzp):
    result = tzp.localize(time(10, 30), "Europe/Berlin")
    assert isinstance(result, time)
    assert not isinstance(result, datetime)
    assert result.tzinfo is not None
    assert (result.hour, result.minute) == (10, 30)


@pytest.mark.parametrize(
    "value",
    [date(2024, 1, 15), datetime(2024, 1, 15, 10, 30), time(10, 30)],
)
def test_localize_accepts_tzinfo_object(tzp, value):
    """A tzinfo object works the same as a tzid string."""
    tz = tzp.timezone("Europe/Berlin")
    assert tzp.localize(value, tz).tzinfo is not None


def test_localize_date_with_none_returns_naive_datetime(tzp):
    """Regression: date.replace(tzinfo=...) used to raise TypeError."""
    result = tzp.localize(date(2024, 1, 15), None)
    assert isinstance(result, datetime)
    assert result.tzinfo is None


def test_localize_datetime_with_none_removes_timezone(tzp):
    aware = tzp.localize(datetime(2024, 1, 15, 10, 30), "Europe/Berlin")
    result = tzp.localize(aware, None)
    assert isinstance(result, datetime)
    assert result.tzinfo is None


def test_localize_time_with_none_removes_timezone(tzp):
    aware = tzp.localize(time(10, 30), "Europe/Berlin")
    result = tzp.localize(aware, None)
    assert isinstance(result, time)
    assert not isinstance(result, datetime)
    assert result.tzinfo is None


# ------------------------------------------------------------ localize_utc

def test_localize_utc_date_returns_datetime(tzp):
    result = tzp.localize_utc(date(2024, 1, 15))
    assert isinstance(result, datetime)
    assert result.tzinfo is not None
    assert result.utcoffset().total_seconds() == 0
    assert (result.hour, result.minute, result.second) == (0, 0, 0)


def test_localize_utc_datetime_returns_datetime(tzp):
    result = tzp.localize_utc(datetime(2024, 1, 15, 10, 30))
    assert isinstance(result, datetime)
    assert result.utcoffset().total_seconds() == 0
    assert (result.hour, result.minute) == (10, 30)


def test_localize_utc_time_returns_time(tzp):
    """Regression: localize_utc used to cast a time straight to datetime."""
    result = tzp.localize_utc(time(10, 30))
    assert isinstance(result, time)
    assert not isinstance(result, datetime)
    assert result.tzinfo is not None
    assert result.utcoffset().total_seconds() == 0
    assert (result.hour, result.minute) == (10, 30)


def test_localize_utc_converts_aware_datetime(tzp):
    berlin = tzp.localize(datetime(2024, 1, 15, 10, 30), "Europe/Berlin")
    result = tzp.localize_utc(berlin)
    assert result.utcoffset().total_seconds() == 0
    assert result.hour == 9  # Berlin is UTC+1 in January


def test_localize_and_localize_utc_agree_on_accepted_types(tzp):
    """Both methods must accept the same three input types."""
    for value in (date(2024, 1, 15), datetime(2024, 1, 15, 10, 30), time(10, 30)):
        tzp.localize(value, "UTC")
        tzp.localize_utc(value)