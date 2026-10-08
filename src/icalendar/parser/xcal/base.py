"""xCal parser class to make sure we parse the content fully."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from icalendar.error import XCalParsingError
from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.adapter import ChildElementAdapter, ElementAdapter

if TYPE_CHECKING:
    from collections.abc import Sequence
    from xml.etree.ElementTree import Element


class InvalidParserState(Exception):
    """The parser is in an invalid state.

    This exception should never be raised in production code.
    """


class XCalParser:
    """Create a new XCalParser that takes care of the parsing state.

    For components:

        .. code-block:: xml

            <icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
              <vcalendar>
                ...
              </vcalendar>
            </icalendar>

    .. code-block:: xml

            <components>
                <vevent>
                ...
                </vevent>
            </components>


    """

    def __init__(self, element: Element | ElementAdapter) -> None:
        self._element = ElementAdapter.with_element(element)
        self._children = self._element.children
        self._consumed = 0
        self._element_is_parsed = False

    @property
    def element(self) -> ElementAdapter:
        """The element to parse."""
        return self._element

    def is_finished(self) -> bool:
        """Whether there are more elements left to consume."""
        return len(self._children) == 0

    @property
    def child(self) -> ChildElementAdapter:
        """Get the next child element.

        Raises:
            InvalidParserState: If there are no more children.
        """
        if self.is_finished():
            raise InvalidParserState("No more children available.")
        return self._children[0]

    def done(self):
        """Done with this child element.

        Raises:
            InvalidParserState: If there are no more children.
        """
        if self.is_finished():
            raise InvalidParserState("No more children available.")
        self._children = self._children[1:]
        self._consumed += 1

    @property
    def tag(self) -> str:
        """The tag of the element we work on."""
        return self._element.tag

    @staticmethod
    def _sanitize_tags(tags: str | Sequence[str]) -> set[str]:
        """Return a set of tags to test."""
        if isinstance(tags, str):
            return {tags.lower()}
        return {t.lower() for t in tags}

    def parse_optional_tag(self, tag: str | Sequence[str]) -> ElementAdapter | None:
        """Find a child tag and return it. or None

        This child is then considered parsed.
        """
        tags = self._sanitize_tags(tag)
        return self._parse_tag(tags)

    def parse_tag(self, tag: str | Sequence[str] | None = None) -> ElementAdapter:
        """Find a child tag and return it.

        This child is then considered parsed.

        Returns:
            The child element with the tag or if no tag is given, the first child.

        Raises:
            XCalParsingError: If the tag is not found.
        """
        if tag is None:
            child = self.child
            self.done()
            return child
        tags = self._sanitize_tags(tag)
        element = self._parse_tag(tags)

        if element is None:
            raise XCalParsingError(
                f"Tag {' or '.join(tags)} not found", None, self._element
            )
        return element

    def _parse_tag(self, tags: set[str]) -> ElementAdapter | None:
        """Find a child tag and return it.

        This child is then considered parsed.
        """
        for i, child in enumerate(self._children):
            if child.tag in tags:
                del self._children[i]
                self._consumed += 1
                return child
        if not self._element_is_parsed and self._element.tag in tags:
            self._element_is_parsed = True
            self._consumed += 1
            return self._element
        return None

    def parse_tags(self, tag: str | Sequence[str]) -> list[ElementAdapter]:
        """Find all child tags and return it.

        These children is then considered parsed.
        """
        tags = self._sanitize_tags(tag)
        children = []
        while True:
            child = self._parse_tag(tags)
            if child is None:
                break
            children.append(child)
        return children

    def ensure_tag_is_present(self, tag: str | Sequence[str]) -> str:
        """Make sure a a tag is present and can be parsed.

        Returns:
            The tag that is present.

        Raises:
            XCalParsingError: If the tag is not found.
        """
        tags = self._sanitize_tags(tag)
        if not self._element_is_parsed and self._element.tag in tags:
            return self._element.tag
        for child in self._children:
            if child.tag in tags:
                return child.tag
        raise XCalParsingError(
            f"Tag {' or '.join(tags)} not found", None, self._element
        )

    def parse_parameters(self) -> Parameters:
        """Return empty parameters as parameters can only appear in a property."""
        return Parameters()


__all__ = ["XCalParser"]
