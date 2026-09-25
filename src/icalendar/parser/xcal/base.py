"""xCal parser class to make sure we parse the content fully."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.xcal.adapter import ChildElementAdapter, ElementAdapter

if TYPE_CHECKING:
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

    def is_finished(self) -> bool:
        """Wether there are more elements left to consume."""
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

    @property
    def tag(self) -> str:
        """The tag of the element we work on."""
        return self._element.tag


__all__ = ["XCalParser"]
