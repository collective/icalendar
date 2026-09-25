from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

REGEX_WHITESPACE = re.compile(r"\s+", re.MULTILINE)


class ElementAdapter:
    """An adapter class with convenience methods for elements."""

    @classmethod
    def with_element(cls, element: Element | ElementAdapter) -> ElementAdapter:
        """Create a new element adapter."""
        if isinstance(element, ElementAdapter):
            return element
        return cls(element)

    def __init__(self, element: Element) -> None:
        self._element = element

    @property
    def element(self) -> Element:
        """The underlying element."""
        return self._element

    @property
    def tag(self) -> str:
        """A sanitized element tag."""
        return self._element.tag.split("}")[-1].lower()

    @property
    def children(self) -> list[ChildElementAdapter]:
        """A list of child elements."""
        return [ChildElementAdapter(child, self) for child in self._element]

    def get_child_with_tag(self, tag: str) -> ChildElementAdapter | None:
        """Get the first child element with the given tag."""
        tag = tag.lower()
        # TODO: Test that this is the only child - we do not expect many of these.
        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def get_xsd_string(self) -> str:
        """Return the element's text as xsd:string.

        This is the only datatype that leaves all the whitespace. -
        `xmlschemata.org <https://books.xmlschemata.org/relaxng/ch19-77303.html>`_
        """
        return self._element.text or ""  # TODO: test

    def get_xsd_token(self) -> str:
        """Return the element's text as xsd:token.

        xsd:token is the most appropriate datatype to use for strings
        that don't care about whitespace. -
        `xmlschemata.org <https://books.xmlschemata.org/relaxng/ch19-77319.html>`_
        """
        return REGEX_WHITESPACE.sub(" ", self.get_xsd_string()).strip()  # TODO: test


class ChildElementAdapter(ElementAdapter):
    """An adapter class with convenience methods for child elements."""

    def __init__(self, child: Element, parent: ElementAdapter) -> None:
        super().__init__(child)
        self._parent = parent

    @property
    def parent(self) -> ElementAdapter:
        """The parent element."""
        return self._parent
