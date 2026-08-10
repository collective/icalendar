"""PERIOD property type from :rfc:`5545`."""

from datetime import date, datetime, timedelta, tzinfo
from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.timezone import tzp
from icalendar.tools import is_date, is_datetime, is_pytz, normalize_pytz, to_datetime

from .base import TimeBase
from .datetime import vDatetime
from .duration import vDuration


def _to_midnight(dt: date, tz: tzinfo | None) -> datetime:
    """Convert a date to the datetime at midnight.

    Parameters:
        dt: The date to convert.
        tz: The timezone of the result, or ``None`` for a naive result.

    Returns:
        The datetime at midnight.
    """
    midnight = to_datetime(dt)
    if tz is None:
        return midnight
    if is_pytz(tz):
        return tz.localize(midnight)  # type: ignore[attr-defined]
    return midnight.replace(tzinfo=tz)


def _to_period_datetimes(
    start: date | datetime, end_or_duration: date | datetime | timedelta
) -> tuple[datetime, datetime | timedelta]:
    """Convert the dates of a period to datetimes.

    :rfc:`5545#section-3.3.9` builds a period from datetimes only, but calendars in the
    wild use dates. A date becomes midnight so that the period can be used
    and written back out.

    A converted half takes the timezone of the other half. Without this, an
    aware and a naive datetime could not be subtracted to compute the
    duration.

    Parameters:
        start: The start of the period.
        end_or_duration: The end of the period or its duration.

    Returns:
        The start and the end or duration, with any date converted.
    """
    if is_date(start):
        start = _to_midnight(start, getattr(end_or_duration, "tzinfo", None))
    if is_date(end_or_duration):
        end_or_duration = _to_midnight(end_or_duration, getattr(start, "tzinfo", None))
    return start, end_or_duration


class vPeriod(TimeBase):
    """A span of time, written either as a start and an end or as a start and a duration.

    The value is a tuple of two :class:`datetime.datetime` objects, or of a
    datetime and a :class:`datetime.timedelta`. Whichever way it was written,
    :attr:`start`, :attr:`end`, and :attr:`duration` are all available, and
    :attr:`by_duration` says which of the two forms is written back out.

    Conforming with :rfc:`5545#section-3.3.9`, a period is built from datetimes
    only, the start must come before the end, and a duration must be positive.
    A half written as a date does not conform. Such a half is read as midnight,
    in the timezone of the other half where it has one, so that a calendar that
    gets this wrong can still be read and written.

    ``FREEBUSY`` holds periods directly. ``RDATE`` holds them through
    :class:`~icalendar.prop.dt.list.vDDDLists`, which splits a comma separated
    list and hands each value to :class:`~icalendar.prop.dt.types.vDDDTypes`.
    The halves themselves are parsed by
    :class:`~icalendar.prop.dt.datetime.vDatetime` and
    :class:`~icalendar.prop.dt.duration.vDuration`.

    Parameters:
        per: The start of the period, and either its end or its duration.
        params: The parameters of the property.

    Raises:
        TypeError: If the start is not a date or a datetime, or if the end is
            not a date, a datetime, or a duration.
        ValueError: If the start is after the end.

    Examples:
        A period from 18:00:00 UTC on January 1, 1997 to 07:00:00 UTC on
        January 2, 1997, and one that starts at 18:00:00 UTC and lasts 5 hours
        and 30 minutes:

        .. code-block:: ics

            19970101T180000Z/19970102T070000Z
            19970101T180000Z/PT5H30M

        .. code-block:: pycon

            >>> from icalendar.prop import vPeriod
            >>> period = vPeriod.from_ical("19970101T180000Z/19970102T070000Z")
            >>> vPeriod(period).to_ical()
            b'19970101T180000Z/19970102T070000Z'
            >>> period = vPeriod.from_ical("19970101T180000Z/PT5H30M")
            >>> vPeriod(period).duration
            datetime.timedelta(seconds=19800)

        A half written as a date is read as midnight:

        .. code-block:: pycon

            >>> vPeriod(vPeriod.from_ical("19970101/19970102")).to_ical()
            b'19970101T000000/19970102T000000'

    ..  versionchanged:: 7.2.3

        A period written with dates is read as midnight.
    """

    default_value: ClassVar[str] = "PERIOD"
    params: Parameters
    #: Whether the value is written as a duration rather than as an end.
    by_duration: bool
    #: The start of the period.
    start: datetime
    #: The end of the period, computed from the duration where there is one.
    end: datetime
    #: The time between the start and the end.
    duration: timedelta

    def __init__(
        self,
        per: tuple[date | datetime, date | datetime | timedelta],
        params: dict[str, Any] | None = None,
    ) -> None:
        start, end_or_duration = per
        if not (isinstance(start, (datetime, date))):
            raise TypeError("Start value MUST be a datetime or date instance")
        if not (isinstance(end_or_duration, (datetime, date, timedelta))):
            raise TypeError(
                "end_or_duration MUST be a datetime, date or timedelta instance"
            )
        start, end_or_duration = _to_period_datetimes(start, end_or_duration)
        by_duration = isinstance(end_or_duration, timedelta)
        if by_duration:
            duration = end_or_duration
            end = normalize_pytz(start + duration)
        else:
            end = end_or_duration
            duration = normalize_pytz(end - start)
        if start > end:
            raise ValueError("Start time is greater than end time")

        self.params = Parameters(params or {"value": "PERIOD"})
        # set the timezone identifier
        # does not support different timezones for start and end
        self.params.update_tzid_from(start)

        self.start = start
        self.end = end
        self.by_duration = by_duration
        self.duration = duration

    def overlaps(self, other):
        if self.start > other.start:
            return other.overlaps(self)
        return self.start <= other.start < self.end

    def to_ical(self):
        if self.by_duration:
            return (
                vDatetime(self.start).to_ical()
                + b"/"
                + vDuration(self.duration).to_ical()
            )
        return vDatetime(self.start).to_ical() + b"/" + vDatetime(self.end).to_ical()

    @staticmethod
    def from_ical(ical, timezone=None):
        from icalendar.prop.dt.types import vDDDTypes

        try:
            start, end_or_duration = ical.split("/")
            start = vDDDTypes.from_ical(start, timezone=timezone)
            end_or_duration = vDDDTypes.from_ical(end_or_duration, timezone=timezone)
        except Exception as e:
            raise ValueError(f"Expected period format, got: {ical}") from e
        return _to_period_datetimes(start, end_or_duration)

    def __repr__(self):
        p = (self.start, self.duration) if self.by_duration else (self.start, self.end)
        return f"vPeriod({p!r})"

    @property
    def dt(self):
        """Make this cooperate with the other vDDDTypes."""
        return (self.start, (self.duration if self.by_duration else self.end))

    @property
    def ical_value(self) -> tuple[datetime, timedelta | datetime]:
        """
        Returns the period as a tuple of its start datetime
        and either its end datetime or duration.
        """
        return self.dt

    from icalendar.param import FBTYPE

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vPeriod."""
        return [
            vPeriod((datetime(2025, 11, 10, 16, 35), timedelta(hours=1, minutes=30))),
            vPeriod((datetime(2025, 11, 10, 16, 35), datetime(2025, 11, 10, 18, 5))),
        ]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        value = [vDatetime(self.start).to_jcal(name)[-1]]
        if self.by_duration:
            value.append(vDuration(self.duration).to_jcal(name)[-1])
        else:
            value.append(vDatetime(self.end).to_jcal(name)[-1])
        return [name, self.params.to_jcal(exclude_utc=True), self.VALUE.lower(), value]

    @classmethod
    def parse_jcal_value(
        cls, jcal: str | list
    ) -> tuple[datetime, datetime] | tuple[datetime, timedelta]:
        """Parse a jCal value.

        Raises:
            ~error.JCalParsingError: If the period is not a list with exactly two items,
                or it can't parse a date-time or duration.
        """
        if isinstance(jcal, str) and "/" in jcal:
            # only occurs in the example of RFC7265, Section B.2.2.
            jcal = jcal.split("/")
        if not isinstance(jcal, list) or len(jcal) != 2:
            raise JCalParsingError(
                "A period must be a list with exactly 2 items.", cls, value=jcal
            )
        with JCalParsingError.reraise_with_path_added(0):
            start = vDatetime.parse_jcal_value(jcal[0])
        with JCalParsingError.reraise_with_path_added(1):
            JCalParsingError.validate_value_type(jcal[1], str, cls)
            if jcal[1].startswith(("P", "-P", "+P")):
                end_or_duration = vDuration.parse_jcal_value(jcal[1])
            else:
                try:
                    end_or_duration = vDatetime.parse_jcal_value(jcal[1])
                except JCalParsingError as e:
                    raise JCalParsingError(
                        "Cannot parse date-time or duration.",
                        cls,
                        value=jcal[1],
                    ) from e
        return start, end_or_duration

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            start, end_or_duration = cls.parse_jcal_value(jcal_property[3])
        params = Parameters.from_jcal_property(jcal_property)
        tzid = params.tzid

        if tzid:
            start = tzp.localize(start, tzid)
            if is_datetime(end_or_duration):
                end_or_duration = tzp.localize(end_or_duration, tzid)

        return cls((start, end_or_duration), params=params)


__all__ = ["vPeriod"]
