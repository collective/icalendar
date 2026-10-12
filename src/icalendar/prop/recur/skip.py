"""SKIP value type of RECUR from :rfc:`7529`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, SubElement

from icalendar.compatibility import Self  # noqa: TC001
from icalendar.enums import Enum
from icalendar.error import JCalParsingError, XCalParsingError
from icalendar.parser.xcal.wrapper import from_xcal_wrapper
from icalendar.prop.text import vText

if TYPE_CHECKING:
    from icalendar.parser.parameter import Parameters
    from icalendar.parser.xcal.base import XCalParser


class vSkip(vText, Enum):
    """Skip values for RRULE.

    These are defined in :rfc:`7529`.

    OMIT  is the default value.

    Examples:

    .. code-block:: pycon

        >>> from icalendar import vSkip
        >>> vSkip.OMIT
        vSkip('OMIT')
        >>> vSkip.FORWARD
        vSkip('FORWARD')
        >>> vSkip.BACKWARD
        vSkip('BACKWARD')
    """

    OMIT = "OMIT"
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"

    __reduce_ex__ = Enum.__reduce_ex__

    def __repr__(self):
        return f"{self.__class__.__name__}({self._name_!r})"

    @classmethod
    def parse_jcal_value(cls, value: Any) -> Self:
        """Parse a jCal value for vSkip.

        Raises:
            ~error.JCalParsingError: If the value is not a valid skip value.
        """
        JCalParsingError.validate_value_type(value, str, cls)
        try:
            return cls[value.upper()]
        except KeyError as e:
            raise JCalParsingError(
                "The value must be a valid skip value.", cls, value=value
            ) from e

    @classmethod
    @from_xcal_wrapper
    def from_xcal_in_recur(cls, parser: XCalParser, _params: Parameters) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            xml: The XML to parse or a parser.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        child = parser.parse_tag()
        text = child.get_xsd_token()
        try:
            return cls(text.upper())
        except ValueError as e:
            raise XCalParsingError(
                "Expected OMIT|BACKWARD|FORWARD https://datatracker.ietf.org/doc/html/rfc7529#section-4.1",
                text,
                child,
            ) from e

    def to_xcal(self, element: Element) -> None:
        """Add the xCal representation of this property according to :rfc:`6321`."""
        self.params.to_xcal(element)
        skip_element = SubElement(element, "skip")
        skip_element.text = self.name


__all__ = ["vSkip"]
