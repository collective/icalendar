"""Utility functions for icalendar."""

from __future__ import annotations

from datetime import date, datetime, tzinfo


def is_date(dt: date) -> bool:
    """Whether this is a date and not a datetime."""
    return isinstance(dt, date) and not isinstance(dt, datetime)


def is_datetime(dt: date) -> bool:
    """Whether this is a date and not a datetime."""
    return isinstance(dt, datetime)


def to_datetime(dt: date) -> datetime:
    """Make sure we have a datetime, not a date."""
    if is_date(dt):
        return datetime(dt.year, dt.month, dt.day)  # noqa: DTZ001
    return dt


def is_pytz(tz: tzinfo):
    """Whether the timezone requires localize() and normalize()."""
    return hasattr(tz, "localize")


def is_pytz_dt(dt: date):
    """Whether the time requires localize() and normalize()."""
    return is_datetime(dt) and is_pytz(dt.tzinfo)


def normalize_pytz(dt: date):
    """We have to normalize the time after a calculation if we use pytz.

    pytz requires this function to be used in order to correctly calculate the
    timezone's offset after calculations.
    """
    if is_pytz_dt(dt):
        return dt.tzinfo.normalize(dt)
    return dt


__all__ = [
    "is_date",
    "is_datetime",
    "is_pytz",
    "is_pytz_dt",
    "normalize_pytz",
    "to_datetime",
]
