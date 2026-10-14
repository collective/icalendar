"""Utility functions for icalendar."""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from pathlib import Path
from typing import BinaryIO, Literal, cast, overload

# These imports must be available at runtime for get_type_hints().
from icalendar.compatibility import TypeGuard, TypeIs  # noqa: TC001
from icalendar.error import InvalidCalendar


def is_date(dt: date | datetime) -> bool:
    """Check if a value is a date but not a datetime.

    This function distinguishes between ``date`` and ``datetime`` objects,
    returning ``True`` only for pure ``date`` instances.

    Parameters:
        dt: The date or datetime object to check.

    Returns:
        ``True`` if the value is a ``date`` but not a ``datetime``,
        ``False`` otherwise.

    Example:
        .. code-block:: pycon

            >>> from datetime import date, datetime
            >>> from icalendar.tools import is_date
            >>> is_date(date(2024, 1, 15))
            True
            >>> is_date(datetime(2024, 1, 15, 10, 30))
            False
    """
    return isinstance(dt, date) and not isinstance(dt, datetime)


def is_datetime(dt: date | datetime) -> TypeIs[datetime]:
    """Check if a value is a datetime.

    Parameters:
        dt: The date or datetime object to check.

    Returns:
        ``True`` if the value is a ``datetime``, ``False`` if it is
        only a ``date``.

    Example:
        .. code-block:: pycon

            >>> from datetime import date, datetime
            >>> from icalendar.tools import is_datetime
            >>> is_datetime(datetime(2024, 1, 15, 10, 30))
            True
            >>> is_datetime(date(2024, 1, 15))
            False
    """
    return isinstance(dt, datetime)


def to_datetime(dt: date | datetime) -> datetime:
    """Convert a date to a datetime.

    If the input is already a ``datetime``, it is returned unchanged.
    If the input is a ``date``, it is converted to a ``datetime`` at midnight.

    Parameters:
        dt: The date or datetime to convert.

    Returns:
        A ``datetime`` object. If the input was a ``date``, the time
        component will be set to midnight (00:00:00).

    Example:
        .. code-block:: pycon

            >>> from datetime import date, datetime
            >>> from icalendar.tools import to_datetime
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

    Parameters:
        tz: The timezone info object to check.

    Returns:
        ``True`` if the timezone is a pytz timezone (has a ``localize``
        attribute), ``False`` otherwise.
    """
    return hasattr(tz, "localize")


def is_pytz_dt(dt: date | datetime) -> TypeGuard[datetime]:
    """Check if a datetime uses a pytz timezone.

    This function checks whether the datetime has a timezone attached
    and whether that timezone is a pytz timezone requiring special handling.

    Parameters:
        dt: The date or datetime object to check.

    Returns:
        ``True`` if the value is a ``datetime`` with a pytz timezone,
        ``False`` otherwise.
    """
    return is_datetime(dt) and (tzinfo := dt.tzinfo) is not None and is_pytz(tzinfo)


def normalize_pytz(dt: date | datetime) -> date | datetime:
    """Normalize a datetime after calculations when using pytz.

    pytz requires the ``normalize()`` function to be called after arithmetic
    operations to correctly adjust the timezone offset, especially around
    daylight saving time transitions.

    Parameters:
        dt: The date or datetime to normalize.

    Returns:
        The normalized datetime if it uses pytz, otherwise the input unchanged.
    """
    if is_pytz_dt(dt):
        return dt.tzinfo.normalize(dt)  # type: ignore[attr-defined]
    return dt


def _detect_format(data: bytes) -> str:
    """Detect calendar format from the first non-whitespace character."""
    stripped = data.lstrip()
    if not stripped:
        raise InvalidCalendar("Empty input provided.")
    first = stripped[0:1]
    if first == b"[":
        return "jcal"
    if first == b"<":
        return "xcal"
    if first == b"B":
        return "ical"
    raise InvalidCalendar(
        "Could not detect calendar format. Expected jCal ([), xCal (<), or iCal (BEGIN)."
    )


@overload
def parse(
    source: str | bytes | Path | BinaryIO,
    multiple: Literal[False] = False,
) -> Calendar: ...


@overload
def parse(
    source: str | bytes | Path | BinaryIO,
    multiple: Literal[True],
) -> list[Calendar]: ...


def parse(
    source: str | bytes | Path | BinaryIO,
    multiple: bool = False,
) -> Calendar | list[Calendar]:
    """Parse calendar data from various formats into Calendar objects.

    Automatically detects the format based on the first non-whitespace character:
    - ``[`` indicates jCal
    - ``<`` indicates xCal
    - ``B`` (from BEGIN) indicates iCal

    Parameters:
        source: Calendar data as a string, bytes, path to a file, or file-like object.
        multiple: If ``True``, returns a list of calendars. If ``False``, returns
            a single calendar. When ``multiple`` is ``False`` and multiple calendars
            are present, only the first is returned.

    Returns:
        A single ``Calendar`` or a list of ``Calendar`` objects depending on ``multiple``.

    Raises:
        ~error.InvalidCalendar: If the input is empty or the format cannot be detected.
        ~error.JCalParsingError: If jCal data is invalid.
        ~error.XCalParsingError: If xCal data is invalid.
        ~error.ICalParsingError: If iCal data is invalid.
        json.JSONDecodeError: If a jCal string is not valid JSON.
        xml.etree.ElementTree.ParseError: If xCal data is not valid XML.

    Example:
        >>> from icalendar import parse
        >>> calendar = parse(b"BEGIN:VCALENDAR\\nVERSION:2.0\\nPRODID:-//Test//EN\\nEND:VCALENDAR")
        >>> calendar.version
        '2.0'
    """
    if isinstance(source, Path):
        data = source.read_bytes()
    elif isinstance(source, str):
        data = source.encode("utf-8")
    elif hasattr(source, "read"):
        data = source.read()
        if isinstance(data, str):
            data = data.encode("utf-8")
    else:
        data = source

    fmt = _detect_format(data)

    from icalendar.cal import Calendar

    if fmt == "jcal":
        text = data.decode("utf-8")
        result = Calendar.from_jcal(text)
        calendars = [result] if not isinstance(result, list) else result
    elif fmt == "xcal":
        calendars = Calendar.from_xcal(data)
    else:  # ical
        result = Calendar.from_ical(data, multiple=True)
        calendars = result if isinstance(result, list) else [result]

    if not calendars:
        raise InvalidCalendar("No calendars found in the input.")

    if multiple:
        return calendars
    return calendars[0]


__all__ = [
    "is_date",
    "is_datetime",
    "is_pytz",
    "is_pytz_dt",
    "normalize_pytz",
    "parse",
    "to_datetime",
]
