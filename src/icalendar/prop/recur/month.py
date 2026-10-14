"""BYMONTH value type of RECUR from :rfc:`5545` and :rfc:`7529`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, SubElement

from icalendar.error import JCalParsingError, XCalParsingError
from icalendar.parser import Parameters
from icalendar.parser.xcal.wrapper import from_xcal_wrapper

if TYPE_CHECKING:
    from icalendar.compatibility import Self
    from icalendar.parser.xcal.base import XCalParser


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
            # ``str.isdigit`` is True for non-ASCII digits (e.g. "١٢") that
            # ``int`` then either accepts as a different value or rejects, so
            # gate on ASCII digits to match what ``int`` parses below.
            if month.isascii() and month.isdigit():
                month_index = int(month)
                leap = False
            else:
                digits = month[:-1]
                if (
                    not month
                    or month[-1] != "L"
                    or not (digits.isascii() and digits.isdigit())
                ):
                    raise ValueError(f"Invalid month: {month!r}")
                month_index = int(digits)
                leap = True
        else:
            leap = False
            month_index = int(month)
        self = super().__new__(cls, month_index)
        self.leap = leap
        self.params = Parameters(params)
        return self

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

    @classmethod
    @from_xcal_wrapper
    def from_xcal(cls, parser: XCalParser, params: Parameters) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            xml: The XML to parse or a parser.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        child = parser.parse_tag()
        text = child.get_xsd_token()
        try:
            return cls(text, params=params)
        except ValueError as e:
            raise XCalParsingError("Expected month number", text, child) from e

    def to_xcal(self, element: Element) -> None:
        """Add the xCal representation of this property according to :rfc:`6321`."""
        self.params.to_xcal(element)
        month_element = SubElement(element, "bymonth")
        month_element.text = str(self)


__all__ = ["vMonth"]
