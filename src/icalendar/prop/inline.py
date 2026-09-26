from typing import Any
from xml.etree.ElementTree import Element

from icalendar.compatibility import Self
from icalendar.error import XCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode


class vInline(str):
    """This is an especially dumb class that just holds raw unparsed text and
    has parameters. Conversion of inline values are handled by the Component
    class, so no further processing is needed.
    """

    params: Parameters
    __slots__ = ("params",)

    def __new__(
        cls,
        value: ICAL_TYPE,
        encoding: str = DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ) -> Self:
        value = to_unicode(value, encoding=encoding)
        if "\r" in value or "\n" in value:
            raise ValueError(
                f"An inline value may not contain CR or LF characters: {value!r}"
            )
        self = super().__new__(cls, value)
        self.params = Parameters(params)
        return self

    def to_ical(self) -> bytes:
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        return cls(ical)

    def to_xcal(self) -> Element:
        """The xCal representation of this property according to :rfc:`6321`.

        Inline values are unparsed text, so they are written as ``<unknown>``,
        the value element :rfc:`6321` uses for values it cannot type.
        """
        element = Element("unknown")
        element.text = str(self)
        return element

    @classmethod
    def from_xcal(cls, element: Element) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            element: The xCal element to parse.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        try:
            return cls(element.text or "")
        except ValueError as e:
            raise XCalParsingError.in_property_text(
                "An inline value may not contain CR or LF characters.", element, cls
            ) from e


__all__ = ["vInline"]
