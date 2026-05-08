"""BYMONTH value type of RECUR from :rfc:`5545` and :rfc:`7529`."""

from typing import Any

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters


class vMonth(int):
    """The number of the month for recurrence.

    In :rfc:`5545`, this is just an int.
    In :rfc:`7529`, this can be followed by `L` to indicate a leap month.

    .. code-block:: pycon

        >>> from icalendar import vMonth
        >>> vMonth(1) # first month January
        vMonth('1')
        >>> vMonth("5L") # leap month in Hebrew calendar
        vMonth('5L')
        >>> vMonth(1).leap
        False
        >>> vMonth("5L").leap
        True

    Definition from RFC:

    .. code-block:: text

        type-bymonth = element bymonth {
           xsd:positiveInteger |
           xsd:string
        }
    """

    params: Parameters

    def __new__(cls, month: str | int, /, params: dict[str, Any] | None = None):
        if isinstance(month, vMonth):
            return cls(month.to_ical().decode())
        if isinstance(month, str):
            if month.isdigit():
                month_index = int(month)
                leap = False
            else:
                if not month or month[-1] != "L" or not month[:-1].isdigit():
                    raise ValueError(f"Invalid month: {month!r}")
                month_index = int(month[:-1])
                leap = True
        else:
            leap = False
            month_index = int(month)
        self = super().__new__(cls, month_index)
        self.leap = leap
        self.params = Parameters(params)
        return self

    @property
    def ical_value(self) -> int:
        """Return the Python int value.

        This property provides access to the underlying month number as an integer.
        The leap month indicator is not included in the integer value; use the
        :attr:`leap` property to check if this is a leap month.

        Returns:
            int: The month number (1-12 for standard months).

        Example:
            >>> from icalendar.prop import vMonth
            >>> m = vMonth(5)
            >>> m.ical_value
            5
            >>> m_leap = vMonth("5L")
            >>> m_leap.ical_value
            5
            >>> m_leap.leap
            True

        See Also:
            :rfc:`5545#section-3.3.10` for the BYMONTH value type specification.
            :rfc:`7529` for leap month support.
        """
        return int(self)

    def to_ical(self) -> bytes:
        """The ical representation."""
        return str(self).encode("utf-8")

    @classmethod
    def from_ical(cls, ical: str):
        return cls(ical)

    @property
    def leap(self) -> bool:
        """Whether this is a leap month."""
        return self._leap

    @leap.setter
    def leap(self, value: bool) -> None:
        self._leap = value

    def __repr__(self) -> str:
        """repr(self)"""
        return f"{self.__class__.__name__}({str(self)!r})"

    def __str__(self) -> str:
        """str(self)"""
        return f"{int(self)}{'L' if self.leap else ''}"

    @classmethod
    def parse_jcal_value(cls, value: Any) -> Self:
        """Parse a jCal value for vMonth.

        Raises:
            ~error.JCalParsingError: If the value is not a valid month.
        """
        JCalParsingError.validate_value_type(value, (str, int), cls)
        try:
            return cls(value)
        except ValueError as e:
            raise JCalParsingError(
                "The value must be a string or an integer.", cls, value=value
            ) from e


__all__ = ["vMonth"]
