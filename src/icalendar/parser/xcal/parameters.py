from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import XCalParser
from icalendar.prop.factory import TypesFactory

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.parser.xcal.adapter import ElementAdapter


class XCalParametersParser(XCalParser):
    """A parser for <properties>."""

    def __init__(
        self,
        element: Element | ElementAdapter,
        parameters: Parameters | None = None,
        types_factory: TypesFactory | None = None,
    ) -> None:
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
        super().__init__(element)
        self._types_factory = (
            TypesFactory.instance() if types_factory is None else types_factory
        )

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

    def parse_tag(self, tag: str) -> ElementAdapter:
        """Find a child tag and return it.

        This child is then considered parsed.
        """
        tag = tag.lower()
        for i, child in enumerate(self._children):
            if child.tag == tag:
                del self._children[i]
                return child
        raise ValueError(f"Tag {tag} not found.")  # TODO: This is the wrong error.
