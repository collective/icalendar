"""UTC-Offset property type from :rfc:`5545`."""

import re
from datetime import timedelta
from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import ICalParsingError, JCalParsingError
from icalendar.parser import Parameters

UTC_OFFSET_REGEX = re.compile(
    r"^(?P<sign>[+-]?)(?P<hours>[0-9]{2})(?P<minutes>[0-9]{2})(?P<seconds>[0-9]{2})?\Z"
)
UTC_OFFSET_JCAL_REGEX = re.compile(
    r"^(?P<sign>[+-])?(?P<hours>\d\d):(?P<minutes>\d\d)(?::(?P<seconds>\d\d))?\Z"
)


class vUTCOffset:
    """UTC Offset

    Value Name:
        UTC-OFFSET

    Purpose:
        This value type is used to identify properties that contain
        an offset from UTC to local time.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            utc-offset = time-numzone

            time-numzone = ("+" / "-") time-hour time-minute [time-second]

    Description:
        The PLUS SIGN character MUST be specified for positive
        UTC offsets (i.e., ahead of UTC).  The HYPHEN-MINUS character MUST
        be specified for negative UTC offsets (i.e., behind of UTC).  The
        value of "-0000" and "-000000" are not allowed.  The time-second,
        if present, MUST NOT be 60; if absent, it defaults to zero.

        Example:
            The following UTC offsets are given for standard time for
            New York (five hours behind UTC) and Geneva (one hour ahead of
            UTC):

        .. code-block:: ics

            -0500

            +0100

        .. code-block:: pycon

            >>> from icalendar.prop import vUTCOffset
            >>> utc_offset = vUTCOffset.from_ical('-0500')
            >>> utc_offset
            datetime.timedelta(days=-1, seconds=68400)
            >>> utc_offset = vUTCOffset.from_ical('+0100')
            >>> utc_offset
            datetime.timedelta(seconds=3600)
    """

    default_value: ClassVar[str] = "UTC-OFFSET"
    params: Parameters

    ignore_exceptions = False  # if True, and we cannot parse this

    # component, we will silently ignore
    # it, rather than let the exception
    # propagate upwards

    def __init__(self, td: timedelta, /, params: dict[str, Any] | None = None) -> None:
        if not isinstance(td, timedelta):
            raise TypeError("Offset value MUST be a timedelta instance")
        self.td = td
        self.params = Parameters(params)

    def to_ical(self) -> str:
        """Return the ical representation."""
        return self.format("")

    def format(self, divider: str = "") -> str:
        """Represent the value with a possible divider.

        .. code-block:: pycon

            >>> from icalendar import vUTCOffset
            >>> from datetime import timedelta
            >>> utc_offset = vUTCOffset(timedelta(hours=-5))
            >>> utc_offset.format()
            '-0500'
            >>> utc_offset.format(divider=':')
            '-05:00'
        """
        if self.td < timedelta(0):
            sign = "-%s"
            td = timedelta(0) - self.td  # get timedelta relative to 0
        else:
            # Google Calendar rejects '0000' but accepts '+0000'
            sign = "+%s"
            td = self.td

        days, seconds = td.days, td.seconds

        hours = abs(days * 24 + seconds // 3600)
        minutes = abs((seconds % 3600) // 60)
        seconds = abs(seconds % 60)
        if seconds:
            duration = f"{hours:02}{divider}{minutes:02}{divider}{seconds:02}"
        else:
            duration = f"{hours:02}{divider}{minutes:02}"
        return sign % duration

    @classmethod
    def from_ical(cls, ical):
        """Parse a UTC offset from its iCalendar representation.

        :rfc:`5545#section-3.3.14` defines the format as a sign, two digits
        for the hours, two digits for the minutes, and two optional digits
        for the seconds:

        .. code-block:: text

            utc-offset = time-numzone

            time-numzone = ("+" / "-") time-hour time-minute [time-second]

        The RFC requires the sign.
        A value without a sign is accepted and read as a positive offset.
        Seconds may be ``60``, which is read as one more minute.

        Parameters:
            ical: The UTC offset to parse, such as ``+0100`` or ``-053000``.
                A :class:`vUTCOffset` is also accepted.

        Returns:
            The offset as a :class:`datetime.timedelta`.
            It is negative for offsets behind UTC.

        Raises:
            TypeError: If ``ical`` is neither a :class:`str` nor a
                :class:`vUTCOffset`.
            ~icalendar.error.ICalParsingError: If ``ical`` does not have the format
                above, or the offset is 24 hours or more, or the minutes are
                greater than 59, or the seconds are greater than 60.
                The range checks are skipped if ``ignore_exceptions``
                is ``True``.

        Example:
            .. code-block:: pycon

                >>> from icalendar import vUTCOffset
                >>> vUTCOffset.from_ical("+0100")
                datetime.timedelta(seconds=3600)
                >>> vUTCOffset.from_ical("0530")
                datetime.timedelta(seconds=19800)
                >>> vUTCOffset.from_ical("-000030")
                datetime.timedelta(days=-1, seconds=86370)
        """
        if isinstance(ical, cls):
            return ical.td
        if not isinstance(ical, str):
            raise TypeError(
                f"UTC offset must be a str or vUTCOffset, not {type(ical).__name__}"
            )
        match = UTC_OFFSET_REGEX.match(ical)
        if match is None:
            raise ICalParsingError("Expected UTC offset as [+-]HHMM[SS]", value=ical)
        hours = int(match.group("hours"))
        minutes = int(match.group("minutes"))
        seconds = int(match.group("seconds") or 0)
        offset = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if not cls.ignore_exceptions:
            if offset >= timedelta(hours=24):
                raise ICalParsingError(
                    "UTC offset must be less than 24 hours", value=ical
                )
            if minutes > 59 or seconds > 60:
                raise ICalParsingError(
                    "UTC offset minutes must be less than 60 "
                    "and seconds less than or equal to 60",
                    value=ical,
                )
        if match.group("sign") == "-":
            return -offset
        return offset

    def __eq__(self, other):
        if not isinstance(other, vUTCOffset):
            return False
        return self.td == other.td

    def __hash__(self):
        return hash(self.td)

    def __repr__(self):
        return f"vUTCOffset({self.td!r})"

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vUTCOffset."""
        return [
            cls(timedelta(hours=3)),
            cls(timedelta(0)),
        ]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), self.format(":")]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        match = UTC_OFFSET_JCAL_REGEX.match(jcal_property[3])
        if match is None:
            raise JCalParsingError(f"Cannot parse {jcal_property!r} as UTC-OFFSET.")
        negative = match.group("sign") == "-"
        hours = int(match.group("hours"))
        minutes = int(match.group("minutes"))
        seconds = int(match.group("seconds") or 0)
        t = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if negative:
            t = -t
        return cls(t, Parameters.from_jcal_property(jcal_property))


__all__ = ["vUTCOffset"]
