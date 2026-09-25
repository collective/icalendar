from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.error import XCalParsingError
from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import XCalParser

if TYPE_CHECKING:
    from collections.abc import Sequence
    from xml.etree.ElementTree import Element

    from icalendar.parser.xcal.adapter import ElementAdapter
    from icalendar.prop.factory import TypesFactory


class XCalParametersParser(XCalParser):
    """A parser for <properties>."""

    def __init__(
        self,
        element: Element | ElementAdapter,
        parameters: Parameters | None = None,
        types_factory: TypesFactory | None = None,
    ) -> None:
        from icalendar.prop.factory import TypesFactory

        super().__init__(element)
        self._types_factory = (
            TypesFactory.instance() if types_factory is None else types_factory
        )
        self._parameters = Parameters() if parameters is None else parameters

    def parse_parameters(self) -> Parameters:
        """Parse properties until finished."""
        while not self.is_finished():
            self.parse_parameter()
        return self._parameters

    def parse_parameter(self):
        """Parse one parameter from the list.

        Example:

            .. code-block:: xml

                <parameters>
                    <tzid>
                        <text>US/Eastern</text>
                    </tzid>
                </parameters>

        """
        self._types_factory.for_property(self.tag, self.child.tag)
        parameters_parser = XCalParameterParser(self.child, self._types_factory)
        values = []
        while not parameters_parser.is_finished():
            values.append(parameters_parser.parse_parameter())
        self._parameters[self.child.tag] = values[0] if len(values) == 1 else values
        self.done()


class XCalParameterParser(XCalParser):
    """A parser for one parameter."""

    def __init__(
        self,
        element: Element | ElementAdapter,
        types_factory: TypesFactory | None = None,
    ) -> None:
        from icalendar.prop.factory import TypesFactory

        super().__init__(element)
        self._types_factory = (
            TypesFactory.instance() if types_factory is None else types_factory
        )
        self._element_is_parsed = False

    def parse_parameter(self) -> None:
        """Parse one parameter value if present.

        Returns:
            The parsed parameters.

        Example:

        .. code-block:: xml

            <tzid>
                <text>US/Eastern</text>
            </tzid>
        """
        # TODO: Test that something is getting consumed
        #       otherwise we might land in a loop
        value_type = self._types_factory.for_property(self.tag, self.child.tag)
        return value_type.from_xcal(self)

    def parse_parameters(self) -> Parameters:
        """Return empty parameters as parameters can only appear in a property."""
        return Parameters()

    @staticmethod
    def _sanitize_tags(tags: str | Sequence[str]) -> set[str]:
        """Return a set of tags to test."""
        if isinstance(tags, str):
            return {tags.lower()}
        return {t.lower() for t in tags}

    def parse_tag(self, tag: str | Sequence[str]) -> ElementAdapter:
        """Find a child tag and return it.

        This child is then considered parsed.

        Raises:
            XCalParsingError: If the tag is not found.
        """
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
        if not self._element_is_parsed and self._element.tag in tags:
            self._element_is_parsed = True
            return self._element
        for i, child in enumerate(self._children):
            if child.tag in tags:
                del self._children[i]
                return child
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
