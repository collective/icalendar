"""Utility functions for icalendar."""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from typing import Union, cast

try:
    from typing import TypeIs
except ImportError:
    from typing_extensions import TypeIs


def is_date(dt: Union[date, datetime]) -> bool:
    """Whether this is a date and not a datetime."""
    return isinstance(dt, date) and not isinstance(dt, datetime)


def is_datetime(dt: Union[date, datetime]) -> TypeIs[datetime]:
    """Whether this is a datetime and not just a date."""
    return isinstance(dt, datetime)


def to_datetime(dt: Union[date, datetime]) -> datetime:
    """Make sure we have a datetime, not a date."""
    if is_date(dt):
        return datetime(dt.year, dt.month, dt.day)  # noqa: DTZ001
    return cast("datetime", dt)


def is_pytz(tz: tzinfo) -> bool:
    """Whether the timezone requires localize() and normalize()."""
    return hasattr(tz, "localize")


def is_pytz_dt(dt: Union[date, datetime]) -> TypeIs[datetime]:
    """Whether the time requires localize() and normalize()."""
    return is_datetime(dt) and (tzinfo := dt.tzinfo) is not None and is_pytz(tzinfo)


def normalize_pytz(dt: Union[date, datetime]) -> Union[date, datetime]:
    """We have to normalize the time after a calculation if we use pytz.

    pytz requires this function to be used in order to correctly calculate the
    timezone's offset after calculations.
    """
    if is_pytz_dt(dt):
        return dt.tzinfo.normalize(dt)  # type: ignore[attr-defined]
    return dt


__all__ = [
    "is_date",
    "is_datetime",
    "is_pytz",
    "is_pytz_dt",
    "normalize_pytz",
    "to_datetime",
]
