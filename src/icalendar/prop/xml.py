"""XML values from :rfc:`6321`."""

from __future__ import annotations

import re
import sys
from contextlib import contextmanager, suppress
from copy import copy, deepcopy
from io import BytesIO
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, ParseError, tostring

from icalendar import config
from icalendar.error import InvalidCalendar
from icalendar.parser.xcal.adapter import ElementAdapter
from icalendar.parser.xcal.base import XCalParser
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE

from .text import vText

if TYPE_CHECKING:
    from collections.abc import Iterator

    from icalendar.compatibility import Self

# The text is already decoded, so an encoding in the XML declaration does not apply.
# With ``[^>]*?\s+encoding``, the whitespace run before the attribute is retried
# from every position that the lazy ``[^>]*?`` reaches, so a long run of whitespace
# in the declaration takes quadratic time.
if sys.version_info >= (3, 11):
    # Possessive quantifiers match the declaration as alternating runs of
    # whitespace and other characters that are never given back, so the match is
    # linear and all whitespace before ``encoding`` is removed.
    _DECLARED_ENCODING = re.compile(
        r"""^(\ufeff?<\?xml\s[^\s>]*+(?:\s++[^\s>]++)*?)\s++encoding\s*+=\s*+"""
        r"""("[^"]*+"|'[^']*+')""",
        re.ASCII,
    )
else:
    # A single ``\s`` before ``encoding`` keeps the match linear.
    # The whitespace that stays in the declaration is valid XML.
    _DECLARED_ENCODING = re.compile(
        r"""^(\ufeff?<\?xml\s[^>]*?)\sencoding\s*=\s*("[^"]*"|'[^']*')""",
        re.ASCII,
    )
# Bytes are decoded with the encoding of their XML declaration.
_DECLARED_ENCODING_OF_BYTES = re.compile(
    rb"""^<\?xml\s[^>]*?\sencoding\s*=\s*["']([A-Za-z][A-Za-z0-9._-]*)["']"""
)


def _decode(data: bytes) -> str | bytes:
    """Decode XML bytes with the encoding of their XML declaration, if they have one."""
    match = _DECLARED_ENCODING_OF_BYTES.match(data)
    if match:
        with suppress(LookupError, UnicodeDecodeError):
            return data.decode(match.group(1).decode("ascii"))
    return data


class vXml(vText):
    """The value of the XML property from :rfc:`6321#section-4.2`.

    The XML property embeds an XML element into any component.
    The element is in a namespace other than the iCalendar namespace.
    The default value type is TEXT, so the value is the XML as text.
    XML with the value type BINARY is a :class:`~icalendar.prop.binary.vBinary`.
    Use :attr:`element` to get the XML element.

    In xCal, the XML property does not exist.
    Instead the XML elements are directly copied into the ``<properties>`` element,
    see :rfc:`6321#section-4.1`.
    :mod:`~xml.etree.ElementTree` chooses the namespace prefixes there.

    Two values are equal if their elements have the same tags, attributes
    and text, whatever the namespace prefixes and the order of the attributes.
    Values with a document type, and other strings, are compared as text.

    Parameters:
        value: Required. The XML as a string, bytes, an :class:`~xml.etree.ElementTree.Element`,
            or an :class:`~icalendar.parser.xcal.adapter.ElementAdapter`.
            Bytes are decoded with the encoding of their XML declaration.
            An element adapter keeps its path in the xCal document.
        encoding: The encoding of bytes without an XML declaration.
        params: Optional parameter dictionary for the property.

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
        element = None
        if isinstance(value, bytes):
            value = _decode(value)
        elif isinstance(value, Element):
            element = ElementAdapter(deepcopy(value))
        elif isinstance(value, ElementAdapter):
            element = value
        if element is not None:
            xml = copy(element.element)
            xml.tail = None
            value = tostring(xml, encoding="unicode")
        self = super().__new__(cls, value, encoding, params=params)
        self._normal_form = None
        # TEXT removes control characters. Then the element is not the value.
        self._element = (
            element if element is not None and str.__eq__(self, value) else None
        )
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
        """The XML element of this value.

        Returns:
            A new :class:`~xml.etree.ElementTree.Element` each time this is accessed.

        Raises:
            xml.etree.ElementTree.ParseError: If the value is not XML.
        """
        if self._element is None:
            self._element = ElementAdapter(self._parse())
        element = deepcopy(self._element.element)
        element.tail = None
        return element

    @property
    def ical_value(self) -> Element:
        """The XML element of this value.

        See also:
            :attr:`element`.

        """
        return self.element

    @classmethod
    def from_xcal(cls, xcal: XCalParser | ElementAdapter | Element) -> Self:
        """Parse xCal from :rfc:`6321`.

        An element in a namespace other than the iCalendar namespace
        is the XML element of an XML property per :rfc:`6321#section-4.1`.
        An ``xml`` property element is parsed like other TEXT properties.

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
        element = xcal.element if isinstance(xcal, XCalParser) else xcal
        if isinstance(element, Element):
            element = ElementAdapter(element)
        if element.is_extension:
            return cls(element)
        return super().from_xcal(xcal)

    def to_xcal(self, element: Element) -> None:
        """Copy the attribute :attr:`element` into the parameter ``element``.

        All other property classes in :mod:`icalendar.prop` add children to the ``element`` parameter.
        :class:`vXml` is special because it holds a single XML 1.0 element per :rfc:`6321#section-4.1`.
        Such an element resides directly inside the ``<properties>`` tag.
        Because of this, the tag, attributes, text, and children of ``element``
        are replaced with the XML 1.0 element contained in this object.

        Parameters:
            element: The ``xml`` property element in the xCal properties.

        Raises:
            ~icalendar.error.InvalidCalendar: If the element is not the ``xml``
                property element, the XML property has parameters other than
                ``VALUE``, its value is not XML, or its element either has no namespace
                or has the iCalendar namespace.

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
            raise InvalidCalendar(
                f"{self.__class__.__name__} can only be written to xCal"
                " as the value of the XML property."
            )
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
            name = ElementAdapter(xml).tag
            raise InvalidCalendar(
                f"Cannot write the XML property to xCal: the element {xml.tag!r}"
                " needs a namespace other than the iCalendar namespace."
                f' Add one with the xmlns attribute, for example <{name} xmlns="'
                'http://example.com/ns">.'
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
        its text, its tail, and its number of children.

        Raises:
            xml.etree.ElementTree.ParseError: If the value is not XML.
        """
        root = self._parse() if self._element is None else self._element.element
        elements = []
        stack = [root]
        while stack:
            e = stack.pop()
            attributes = tuple(sorted(e.attrib.items()))
            tail = None if e is root else e.tail
            elements.append((e.tag, attributes, e.text, tail, len(e)))
            stack.extend(reversed(e))
        return tuple(elements)

    def __eq__(self, other: object) -> bool:
        """Compare the XML of two vXml values."""
        if not isinstance(other, vXml):
            return NotImplemented
        return (
            str.__eq__(self, other)
            or self._get_normal_form() == other._get_normal_form()
        )

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
def _preserve_indentation_of_xcal_extension_properties(
    xcal: Element,
) -> Iterator[None]:
    """Keep the whitespace in the elements of XML properties in xCal.

    :func:`xml.etree.ElementTree.indent` changes the whitespace in elements.
    In this context, the elements of XML properties are replaced
    by empty elements.
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
