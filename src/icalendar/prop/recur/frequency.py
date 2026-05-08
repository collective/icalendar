"""FREQ value type of RECUR from :rfc:`5545`."""

from typing import Any

from icalendar.caselessdict import CaselessDict
from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING, to_unicode


class vFrequency(str):
    """A simple class that catches illegal values."""

    params: Parameters
    __slots__ = ("params",)

    frequencies = CaselessDict(
        {
            "SECONDLY": "SECONDLY",
            "MINUTELY": "MINUTELY",
            "HOURLY": "HOURLY",
            "DAILY": "DAILY",
            "WEEKLY": "WEEKLY",
            "MONTHLY": "MONTHLY",
            "YEARLY": "YEARLY",
        }
    )

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        if self not in vFrequency.frequencies:
            raise ValueError(f"Expected frequency, got: {self}")
        self.params = Parameters(params)
        return self

    @property
    def ical_value(self) -> str:
        """Return the Python string value.

        This property provides access to the underlying frequency string value,
        which must be one of the valid recurrence frequencies defined in RFC 5545.

        Returns:
            str: The frequency string value (SECONDLY, MINUTELY, HOURLY, DAILY,
                WEEKLY, MONTHLY, or YEARLY).

        Example:
            >>> from icalendar.prop import vFrequency
            >>> freq = vFrequency("DAILY")
            >>> freq.ical_value
            'DAILY'
            >>> freq2 = vFrequency("WEEKLY")
            >>> freq2.ical_value
            'WEEKLY'

        See Also:
            :rfc:`5545#section-3.3.10` for the FREQ value type specification.
        """
        return str(self)

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING).upper()

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical.upper())
        except Exception as e:
            raise ValueError(f"Expected frequency, got: {ical}") from e

    @classmethod
    def parse_jcal_value(cls, value: Any) -> Self:
        """Parse a jCal value for vFrequency.

        Raises:
            ~error.JCalParsingError: If the value is not a valid frequency.
        """
        JCalParsingError.validate_value_type(value, str, cls)
        try:
            return cls(value)
        except ValueError as e:
            raise JCalParsingError(
                "The value must be a valid frequency.", cls, value=value
            ) from e


__all__ = ["vFrequency"]
