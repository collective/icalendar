from __future__ import annotations

import re
from collections import defaultdict
from xml.etree.ElementTree import Element

from icalendar.error import XCalParsingError
from icalendar.parser.xcal.string import string_to_xsd_float

REGEX_WHITESPACE = re.compile(r"\s+", re.MULTILINE)


class ElementAdapter:
    """An adapter class with convenience methods for XML elements.

    This is a read-only access adapter.
    All operations on ElementAdapter are reproducible and
    do not change the underlying element.
    """

    @classmethod
    def with_element(cls, element: Element | ElementAdapter) -> ElementAdapter:
        """Create a new element adapter or return the present one."""
        if isinstance(element, ElementAdapter):
            return element
        return cls(element)

    def __init__(self, element: Element) -> None:
        self._element = element
        self._tag = self._element.tag.split("}")[-1].lower()

    @property
    def element(self) -> Element:
        """The underlying element."""
        return self._element

    @property
    def tag(self) -> str:
        """A sanitized element tag."""
        return self._tag

    @property
    def children(self) -> list[ChildElementAdapter]:
        """A list of child elements."""
        tags = defaultdict(int)
        children = []
        for child_element in self._element:
            tag = child_element.tag
            tags[tag] += 1
            children.append(ChildElementAdapter(child_element, self, tags[tag]))
        return children

    def get_child_with_tag(self, tag: str) -> ChildElementAdapter | None:
        """Get the first child element with the given tag."""
        tag = tag.lower()
        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def parse_tag(self, tag: str):
        """Get the first child element with the given tag.

        Returns:
            The first child element with the given tag.

        Raises:
            XCalParsingError: If the tag is not found.
        """
        child = self.get_child_with_tag(tag)
        if child is None:
            raise XCalParsingError(f"Tag {tag} not found", None, self)
        return child

    def get_xsd_string(self) -> str:
        """Return the element's text as xsd:string.

        This is the only datatype that leaves all the whitespace. -
        `xmlschemata.org <https://books.xmlschemata.org/relaxng/ch19-77303.html>`_
        """
        return self._element.text or ""

    def get_xsd_token(self) -> str:
        """Return the element's text as xsd:token.

        xsd:token is the most appropriate datatype to use for strings
        that don't care about whitespace. -
        `xmlschemata.org <https://books.xmlschemata.org/relaxng/ch19-77319.html>`_
        """
        return REGEX_WHITESPACE.sub(" ", self.get_xsd_string()).strip()

    def get_text_without_whitespace(self) -> str:
        """Return the element's text with all whitespace removed."""
        return REGEX_WHITESPACE.sub("", self.get_xsd_string())

    def get_xpath(self) -> str:
        """Return the path in the XML file where this element occurs."""
        return f"/{self.tag}"

    def get_xsd_float(self) -> float:
        """Return the element's text parsed as xsd:float.

        Returns:
            The parsed float value.

        Raises:
            XCalParsingError: If the value is not a float.
        """
        try:
            return string_to_xsd_float(self.get_xsd_token())
        except (TypeError, ValueError) as e:
            raise XCalParsingError(
                "Expected xsd:float",
                self.get_xsd_token(),
                self,
            ) from e

    def __repr__(self) -> str:
        """Return the text representation of this element."""
        return f"Element@{self.get_xpath()}"

    def make_parent(self, tag: str) -> ElementAdapter:
        """Return an element adapter for a parent."""
        parent = Element(tag)
        parent.append(self._element)
        return ElementAdapter(parent)

    def get_inner_text(self) -> str:
        """Return the inner text.

        This is useful when there is a broken property.
        """
        return self.get_xsd_string()


class ChildElementAdapter(ElementAdapter):
    """An adapter class with convenience methods for child elements.

    Parameters:
        child: The child element.
        parent: The parent element adapter.
        index: The index for building the XPath in the parent.
    """

    def __init__(self, child: Element, parent: ElementAdapter, index: int = 1) -> None:
        super().__init__(child)
        self._parent = parent
        self._index = index

    @property
    def parent(self) -> ElementAdapter:
        """The parent element."""
        return self._parent

    def get_xpath(self) -> str:
        """Return the path in the XML file where this element occurs."""
        return f"{self.parent.get_xpath()}/{self.tag}[{self._index}]"
