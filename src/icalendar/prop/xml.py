"""XML values from :rfc:`6321`."""

from __future__ import annotations

import base64
from copy import copy
from io import StringIO
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, ParseError, tostring

from icalendar import config
from icalendar.error import JCalParsingError
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode

from .binary import vBinary
from .text import vText

if TYPE_CHECKING:
    from icalendar.compatibility import Self

_XCAL_NAMESPACE = "{urn:ietf:params:xml:ns:icalendar-2.0}"


def _is_extension(element: Element) -> bool:
    """Whether an xCal element is an extension for the XML property.

    See :rfc:`6321#section-4.1`.
    """
    return element.tag.startswith("{") and not element.tag.startswith(_XCAL_NAMESPACE)


class vXml(vText):
    """The value of the XML property from :rfc:`6321#section-4.2`.

    The XML property embeds an XML element into any component.
    The element has a namespace other than the iCalendar namespace.
    In xCal, the element is part of the properties of the component,
    see :rfc:`6321#section-4.1`.

    You can create this value from XML text or from an
    :class:`~xml.etree.ElementTree.Element`.
    The XML is written as TEXT, or in Base64 if the ``ENCODING``
    parameter is ``BASE64`` or the ``VALUE`` parameter is ``BINARY``.

    Examples:
        Add XML to an event and get the XML element.

        .. code-block:: pycon

            >>> from icalendar import Event
            >>> event = Event()
            >>> event.add("XML", '<a xmlns="http://example.com/ns">text</a>')
            >>> print(event.to_ical())
            BEGIN:VEVENT
            XML:<a xmlns="http://example.com/ns">text</a>
            END:VEVENT
            >>> event["XML"].element.tag
            '{http://example.com/ns}a'

        Write the XML in Base64.

        .. code-block:: pycon

            >>> from icalendar import vXml
            >>> xml = vXml(
            ...     '<a xmlns="http://example.com/ns">text</a>',
            ...     params={"ENCODING": "BASE64", "VALUE": "BINARY"},
            ... )
            >>> print(xml.to_ical().decode())
            PGEgeG1sbnM9Imh0dHA6Ly9leGFtcGxlLmNvbS9ucyI+dGV4dDwvYT4=
    """

    def __new__(
        cls,
        value: ICAL_TYPE | Element,
        encoding: str = DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ) -> Self:
        if isinstance(value, Element):
            element = copy(value)
            element.tail = None
            value = tostring(element, encoding="unicode")
        return super().__new__(cls, value, encoding, params=params)

    @property
    def element(self) -> Element:
        """A new XML element parsed from this value.

        Raises:
            xml.etree.ElementTree.ParseError: If the value is not valid XML.
        """
        return config.parse_xml(StringIO(self)).getroot()

    def _is_base64(self) -> bool:
        """Whether the XML is written in Base64."""
        encoding = self.params.get("ENCODING", "")
        return encoding.upper() == "BASE64" or self.params.value == "BINARY"

    def to_ical(self) -> bytes:
        """Serialize the XML as TEXT or in Base64."""
        if self._is_base64():
            return base64.b64encode(self.encode(self.encoding))
        return super().to_ical()

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        """Parse the XML from TEXT or from Base64.

        XML starts with ``<``. Other values are decoded from Base64.

        Raises:
            ValueError: If the value is neither XML nor Base64.
        """
        value = to_unicode(ical)
        if not value.lstrip().startswith("<"):
            value = vBinary.from_ical(value).decode(DEFAULT_ENCODING)
        return cls(value)

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        if self._is_base64():
            return vBinary(self.encode(self.encoding), params=self.params).to_jcal(name)
        return super().to_jcal(name)

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        if jcal_property[2].lower() == "binary":
            binary = vBinary.from_jcal(jcal_property)
            return cls(binary.bytes, params=binary.params)
        return super().from_jcal(jcal_property)

    def _xcal_extension(self) -> Element | None:
        """The XML element to add to the properties in xCal.

        This reverses :rfc:`6321#section-4.1`.
        Return ``None`` if the element would lose information.
        Elements without a namespace do not get the iCalendar namespace.
        """
        if set(self.params) - {"ENCODING", "VALUE"}:
            return None
        try:
            element = self.element
        except ParseError:
            return None
        if not _is_extension(element):
            return None
        if not all(child.tag.startswith("{") for child in element.iter()):
            element.set("xmlns", "")
        return element

    def _normalized(self) -> str:
        """The XML with normalized namespace prefixes for comparison."""
        try:
            return tostring(self.element, encoding="unicode")
        except ParseError:
            return str(self)

    def __eq__(self, other: object) -> bool:
        """Compare the XML, ignoring namespace prefixes."""
        if isinstance(other, vXml):
            return self._normalized() == other._normalized()
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        """The opposite of ``==``."""
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def __hash__(self) -> int:
        """Hash the XML, ignoring namespace prefixes."""
        return hash(self._normalized())

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vXml."""
        return [cls('<a xmlns="http://example.com/ns">Hello World!</a>')]


__all__ = ["vXml"]
