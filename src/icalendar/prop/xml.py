"""XML values from :rfc:`6321`."""

from __future__ import annotations

import re
from contextlib import contextmanager, suppress
from copy import copy, deepcopy
from io import BytesIO
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, ParseError, tostring

from icalendar import config
from icalendar.error import InvalidCalendar
from icalendar.parser.xcal.adapter import ElementAdapter
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE

from .text import vText

if TYPE_CHECKING:
    from collections.abc import Iterator

    from icalendar.compatibility import Self
    from icalendar.parser.xcal.base import XCalParser

# The text is already decoded, so an encoding in the XML declaration does not apply.
_DECLARED_ENCODING = re.compile(
    r"""^(\ufeff?<\?xml\s[^>]*?)\s+encoding\s*=\s*("[^"]*"|'[^']*')""",
    re.ASCII,
)


class vXml(vText):
    """The value of the XML property from :rfc:`6321#section-4.2`.

    The XML property embeds an XML element into any component.
    The element is in a namespace other than the iCalendar namespace.
    The default value type is TEXT, so the value is the XML as text.
    XML with the value type BINARY is a :class:`~icalendar.prop.binary.vBinary`.

    You can create this value from XML text, an
    :class:`~xml.etree.ElementTree.Element`, or an
    :class:`~icalendar.parser.xcal.adapter.ElementAdapter`.
    Use :attr:`element` to get the XML element.

    In xCal, the XML element takes the place of the ``xml`` property element,
    see :rfc:`6321#section-4.1`.
    ElementTree chooses the namespace prefixes there.
    So two values are equal if their elements have the same tags, attributes
    and text, whatever the namespace prefixes and the order of the attributes.
    Values with a document type, and other strings, are compared as text.

    Examples:
        Add XML to an event and get the XML element.

        .. code-block:: pycon

            >>> from icalendar import Event
            >>> event = Event()
            >>> event.add("XML", '<a xmlns="http://example.com/ns">text</a>')
            >>> print(event.to_ical().decode())
            BEGIN:VEVENT
            XML:<a xmlns="http://example.com/ns">text</a>
            END:VEVENT
            >>> event["XML"].element.tag
            '{http://example.com/ns}a'

        In xCal, the element is part of the properties of the event.

        .. code-block:: pycon

            >>> print(event.to_xcal(indent=2).decode())
            <?xml version="1.0" encoding="UTF-8"?>
            <icalendar xmlns:ns0="http://example.com/ns" xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
              <vevent>
                <properties>
                  <ns0:a>text</ns0:a>
                </properties>
              </vevent>
            </icalendar>
    """

    _element: ElementAdapter | None
    _normal_form: tuple | str | None
    __slots__ = ("_element", "_normal_form")

    def __new__(
        cls,
        value: ICAL_TYPE | Element | ElementAdapter,
        encoding: str = DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ) -> Self:
        from_element = isinstance(value, (Element, ElementAdapter))
        if isinstance(value, ElementAdapter):
            value = value.element
        if from_element:
            value = copy(value)
            value.tail = None
            value = tostring(value, encoding="unicode")
        self = super().__new__(cls, value, encoding, params=params)
        self._element = None
        self._normal_form = None
        if from_element:
            # Keep the element parsed from the text, so that both are the same XML.
            with suppress(ParseError, ValueError):
                self._element = ElementAdapter(self._parse())
        return self

    def _parse(self) -> Element:
        """Parse the text of this value as XML.

        Raises:
            xml.etree.ElementTree.ParseError: If the value is not XML.
        """
        text = _DECLARED_ENCODING.sub(r"\1", self, count=1)
        data = text.encode("utf-8", "surrogatepass")
        try:
            return config.parse_xml(BytesIO(data)).getroot()
        except LookupError as error:
            # The XML declaration names an unknown encoding.
            raise ParseError(error) from error

    @property
    def element(self) -> Element:
        """A new XML element of this value.

        Raises:
            xml.etree.ElementTree.ParseError: If the value is not XML.
        """
        if self._element is None:
            return self._parse()
        return deepcopy(self._element.element)

    @classmethod
    def from_xcal(cls, xcal: XCalParser | ElementAdapter | Element) -> Self:
        """Parse xCal from :rfc:`6321`.

        An element in a namespace other than the iCalendar namespace
        is the XML element of an XML property, see :rfc:`6321#section-4.1`.
        Other elements are parsed as TEXT.

        Parameters:
            xcal: The XML to parse or a parser.

        Returns:
            The value of the XML property.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.

        Example:
            .. code-block:: pycon

                >>> from xml.etree.ElementTree import fromstring
                >>> from icalendar import vXml
                >>> vXml.from_xcal(fromstring('<a xmlns="http://example.com/ns">text</a>'))
                vXml(b'<ns0:a xmlns:ns0="http://example.com/ns">text</ns0:a>')
        """
        if isinstance(xcal, Element):
            xcal = ElementAdapter(xcal)
        if isinstance(xcal, ElementAdapter) and xcal.is_extension:
            return cls(xcal)
        return super().from_xcal(xcal)

    def to_xcal(self, element: Element) -> None:
        """Add the xCal representation of this property according to :rfc:`6321`.

        The XML element takes the place of the ``xml`` property element,
        see :rfc:`6321#section-4.1`.
        Other properties write this value as TEXT.

        Parameters:
            element: The property element in the xCal properties.

        Returns:
            ``None``

        Raises:
            ~icalendar.error.InvalidCalendar: If the XML property has parameters
                other than ``VALUE``, its value is not XML, or its element has
                no namespace or the iCalendar namespace.

        Example:
            The ``xml`` property element becomes the XML element.

            .. code-block:: pycon

                >>> from xml.etree.ElementTree import Element, tostring
                >>> from icalendar import vXml
                >>> element = Element("xml")
                >>> vXml('<a xmlns="http://example.com/ns">text</a>').to_xcal(element)
                >>> tostring(element)
                b'<ns0:a xmlns:ns0="http://example.com/ns">text</ns0:a>'
        """
        if element.tag != "xml":
            super().to_xcal(element)
            return
        parameters = set(self.params) - {"VALUE"}
        if parameters:
            raise InvalidCalendar(
                "Cannot write the XML property to xCal with the parameters "
                + ", ".join(sorted(parameters))
            )
        try:
            xml = self.element
        except ParseError as error:
            raise InvalidCalendar(
                f"Cannot write the XML property to xCal: {error}"
            ) from error
        if not ElementAdapter(xml).is_extension:
            raise InvalidCalendar(
                f"Cannot write the XML property to xCal: the element {xml.tag!r}"
                " needs a namespace other than the iCalendar namespace"
            )
        if any(
            isinstance(child.tag, str) and not child.tag.startswith("{")
            for child in xml.iter()
        ):
            # Elements without a namespace do not get the iCalendar namespace.
            xml.set("xmlns", "")
        element.tag = xml.tag
        element.attrib = xml.attrib
        element.text = xml.text
        element[:] = list(xml)

    def _get_normal_form(self) -> tuple | str:
        """What equality compares: the XML elements, or the text.

        The text is compared if the value is not XML, or if it has a document
        type, which could make the XML much larger than the text.
        The normal form is computed once.
        """
        if self._normal_form is None:
            self._normal_form = str(self)
            if "<!DOCTYPE" not in self:
                with suppress(ParseError, ValueError):
                    self._normal_form = self._get_elements()
        return self._normal_form

    def _get_elements(self) -> tuple:
        """The elements of the XML in document order, without recursion.

        Each element has its tag with the namespace, its sorted attributes,
        its text, its tail and its number of children.

        Raises:
            xml.etree.ElementTree.ParseError: If the value is not XML.
        """
        element = self._parse() if self._element is None else self._element.element
        elements = []
        stack = [element]
        while stack:
            e = stack.pop()
            attributes = tuple(sorted(e.attrib.items()))
            elements.append((e.tag, attributes, e.text, e.tail, len(e)))
            stack.extend(reversed(e))
        return tuple(elements)

    def __eq__(self, other: object) -> bool:
        """Compare the XML of two values, or the text with other strings."""
        if isinstance(other, vXml):
            return (
                str.__eq__(self, other)
                or self._get_normal_form() == other._get_normal_form()
            )
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        """The opposite of ``==``."""
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def __hash__(self) -> int:
        """Hash what two vXml values compare."""
        return hash(self._get_normal_form())

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vXml."""
        return [cls('<a xmlns="http://example.com/ns">Hello World!</a>')]


@contextmanager
def _hide_xml_properties(xcal: Element) -> Iterator[None]:
    """Hide the elements of XML properties in xCal.

    :func:`xml.etree.ElementTree.indent` changes the whitespace in elements.
    The elements of XML properties keep their whitespace.
    In this context, they are replaced by empty elements.
    """
    hidden = []
    for properties in xcal.iter("properties"):
        for index, element in enumerate(properties):
            if ElementAdapter(element).is_extension:
                placeholder = Element(element.tag)
                properties[index] = placeholder
                hidden.append((properties, index, element, placeholder))
    try:
        yield
    finally:
        for properties, index, element, placeholder in hidden:
            element.tail = placeholder.tail
            properties[index] = element


__all__ = ["vXml"]
