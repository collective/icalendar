"""TZP.localize and TZP.localize_utc accept date, datetime and time.

date     -> datetime
datetime -> datetime
time     -> time

See https://github.com/collective/icalendar/issues/1802
"""

from datetime import date, datetime, time

import pytest

from icalendar.timezone import tzid_from_tzinfo


def assert_equals_dt(result, expected, tzid=None):
    """Assert result matches expected date/datetime/time and timezone.

    tzid is the expected timezone id, or None if result should be naive.
    """
    assert isinstance(result, type(expected))
    assert result.replace(tzinfo=None) == expected
    if tzid is None:
        assert result.tzinfo is None
    else:
        assert tzid_from_tzinfo(result.tzinfo) == tzid


# ---------------------------------------------------------------- localize

def test_localize_date_returns_datetime(tzp):
    result = tzp.localize(date(2024, 1, 15), "Europe/Berlin")
    assert_equals_dt(result, datetime(2024, 1, 15, 0, 0, 0), "Europe/Berlin")


def test_localize_datetime_returns_datetime(tzp):
    result = tzp.localize(datetime(2024, 1, 15, 10, 30), "Europe/Berlin")
    assert_equals_dt(result, datetime(2024, 1, 15, 10, 30), "Europe/Berlin")


def test_localize_time_returns_time(tzp):
    result = tzp.localize(time(10, 30), "Europe/Berlin")
    assert_equals_dt(result, time(10, 30), "Europe/Berlin")


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
    assert_equals_dt(result, datetime(2024, 1, 15, 0, 0, 0), None)


def test_localize_datetime_with_none_removes_timezone(tzp):
    aware = tzp.localize(datetime(2024, 1, 15, 10, 30), "Europe/Berlin")
    result = tzp.localize(aware, None)
    assert_equals_dt(result, datetime(2024, 1, 15, 10, 30), None)


def test_localize_time_with_none_removes_timezone(tzp):
    aware = tzp.localize(time(10, 30), "Europe/Berlin")
    result = tzp.localize(aware, None)
    assert_equals_dt(result, time(10, 30), None)


# ------------------------------------------------------------ localize_utc

def test_localize_utc_date_returns_datetime(tzp):
    result = tzp.localize_utc(date(2024, 1, 15))
    assert_equals_dt(result, datetime(2024, 1, 15, 0, 0, 0), "UTC")


def test_localize_utc_datetime_returns_datetime(tzp):
    result = tzp.localize_utc(datetime(2024, 1, 15, 10, 30))
    assert_equals_dt(result, datetime(2024, 1, 15, 10, 30), "UTC")


def test_localize_utc_time_returns_time(tzp):
    """Regression: localize_utc used to cast a time straight to datetime."""
    result = tzp.localize_utc(time(10, 30))
    assert_equals_dt(result, time(10, 30), "UTC")


def test_localize_utc_converts_aware_datetime(tzp):
    berlin = tzp.localize(datetime(2024, 1, 15, 10, 30), "Europe/Berlin")
    result = tzp.localize_utc(berlin)
    assert_equals_dt(result, datetime(2024, 1, 15, 9, 30), "UTC")