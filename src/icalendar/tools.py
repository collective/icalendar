"""Utility functions for icalendar."""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from typing import TYPE_CHECKING, Union, cast


if TYPE_CHECKING:
    from icalendar.compatibility import TypeGuard, TypeIs


def is_date(dt: Union[date, datetime]) -> bool:
    """Check if a value is a date but not a datetime.

    This function distinguishes between ``date`` and ``datetime`` objects,
    returning ``True`` only for pure ``date`` instances.

    Args:
        dt: The date or datetime object to check.

    Returns:
        ``True`` if the value is a ``date`` but not a ``datetime``,
        ``False`` otherwise.

    Example:
        >>> from datetime import date, datetime
        >>> is_date(date(2024, 1, 15))
        True
        >>> is_date(datetime(2024, 1, 15, 10, 30))
        False
    """
    return isinstance(dt, date) and not isinstance(dt, datetime)


def is_datetime(dt: Union[date, datetime]) -> TypeIs[datetime]:
    """Check if a value is a datetime.

    Args:
        dt: The date or datetime object to check.

    Returns:
        ``True`` if the value is a ``datetime``, ``False`` if it is
        only a ``date``.

    Example:
        >>> from datetime import date, datetime
        >>> is_datetime(datetime(2024, 1, 15, 10, 30))
        True
        >>> is_datetime(date(2024, 1, 15))
        False
    """
    return isinstance(dt, datetime)


def to_datetime(dt: Union[date, datetime]) -> datetime:
    """Convert a date to a datetime.

    If the input is already a ``datetime``, it is returned unchanged.
    If the input is a ``date``, it is converted to a ``datetime`` at midnight.

    Args:
        dt: The date or datetime to convert.

    Returns:
        A ``datetime`` object. If the input was a ``date``, the time
        component will be set to midnight (00:00:00).

    Example:
        >>> from datetime import date, datetime
        >>> to_datetime(date(2024, 1, 15))
        datetime.datetime(2024, 1, 15, 0, 0)
        >>> to_datetime(datetime(2024, 1, 15, 10, 30))
        datetime.datetime(2024, 1, 15, 10, 30)
    """
    if is_date(dt):
        return datetime(dt.year, dt.month, dt.day)  # noqa: DTZ001
    return cast("datetime", dt)


def is_pytz(tz: tzinfo) -> bool:
    """Check if a timezone is a pytz timezone.

    pytz timezones require special handling with ``localize()`` and
    ``normalize()`` methods for correct timezone calculations.

    Args:
        tz: The timezone info object to check.

    Returns:
        ``True`` if the timezone is a pytz timezone (has a ``localize``
        attribute), ``False`` otherwise.
    """
    return hasattr(tz, "localize")


def is_pytz_dt(dt: Union[date, datetime]) -> TypeGuard[datetime]:
    """Check if a datetime uses a pytz timezone.

    This function checks whether the datetime has a timezone attached
    and whether that timezone is a pytz timezone requiring special handling.

    Args:
        dt: The date or datetime object to check.

    Returns:
        ``True`` if the value is a ``datetime`` with a pytz timezone,
        ``False`` otherwise.
    """
    return is_datetime(dt) and (tzinfo := dt.tzinfo) is not None and is_pytz(tzinfo)


def normalize_pytz(dt: Union[date, datetime]) -> Union[date, datetime]:
    """Normalize a datetime after calculations when using pytz.

    pytz requires the ``normalize()`` function to be called after arithmetic
    operations to correctly adjust the timezone offset, especially around
    daylight saving time transitions.

    Args:
        dt: The date or datetime to normalize.

    Returns:
        The normalized datetime if it uses pytz, otherwise the input unchanged.
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
