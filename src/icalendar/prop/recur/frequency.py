"""FREQ value type of RECUR from :rfc:`5545`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, SubElement

from icalendar.caselessdict import CaselessDict
from icalendar.error import JCalParsingError, XCalParsingError
from icalendar.parser import Parameters
from icalendar.parser.xcal.wrapper import from_xcal_wrapper
from icalendar.parser_tools import DEFAULT_ENCODING, to_unicode

if TYPE_CHECKING:
    from icalendar.compatibility import Self
    from icalendar.parser.xcal.base import XCalParser


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

    @property
    def ical_value(self) -> str:
        """Returns the frequency value as a string, for example, ``WEEKLY`` or ``DAILY``.

        See Also:

            :rfc:`5545#section-3.3.10` for the ``FREQ`` rule grammar.
        """
        return str(self)

    @classmethod
    @from_xcal_wrapper
    def from_xcal(cls, parser: XCalParser, params: Parameters) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            parser: The parser to use.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        child = parser.parse_tag()
        text = child.get_xsd_token()
        try:
            return cls(text, params=params)
        except ValueError as e:
            raise XCalParsingError(
                "Expected frequency https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10",
                text,
                child,
            ) from e

    def to_xcal(self, element: Element) -> None:
        """Add the xCal representation of this property according to :rfc:`6321`."""
        self.params.to_xcal(element)
        frequency_element = SubElement(element, "freq")
        frequency_element.text = str(self)


__all__ = ["vFrequency"]
