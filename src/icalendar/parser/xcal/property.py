from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import InvalidParserState, XCalParser
from icalendar.parser.xcal.parameters import XCalParameterParser, XCalParametersParser

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.cal.component import Component
    from icalendar.parser.xcal.adapter import ElementAdapter
    from icalendar.prop.factory import TypesFactory


class XCalPropertiesParser(XCalParser):
    """A parser for <properties>."""

    def __init__(
        self,
        element: Element | ElementAdapter,
        component: Component,
        types_factory: TypesFactory,
    ) -> None:
        super().__init__(element)
        self._types_factory = types_factory
        self._component = component

    def parse_properties(self):
        """Parse properties until finished."""
        while not self.is_finished():
            self.parse_property()

    def parse_property(self):
        """Parse one property from the list.

        Example:

            .. code-block:: xml

                <properties>
                    <prodid>
                        <text>-//Example Inc.//Example Client//EN</text>
                    </prodid>
                    <version>
                        <text>2.0</text>
                    </version>
                </properties>
        """
        property_parser = XCalPropertyParser(self.child, self._types_factory)
        values = []
        while not property_parser.is_finished():
            values.append(property_parser.parse_property())
        if values:
            previous = self._component.get(self.child.tag)
            if previous is None:
                # first occurrence of the parameter
                self._component[self.child.tag] = (
                    values[0] if len(values) == 1 else values
                )
            # the parameter occurs several times
            elif not isinstance(previous, list):
                # one value
                self._component[self.child.tag] = [previous] + values
            else:
                # several values
                previous.extend(values)
        self.done()


class XCalPropertyParser(XCalParameterParser):
    """A parser for one property.

    This parses the value type and additionally the parameters.
    """

    def __init__(
        self,
        element: Element | ElementAdapter,
        types_factory: TypesFactory | None = None,
    ) -> None:
        super().__init__(element)
        from icalendar.prop.factory import TypesFactory

        self._types_factory = (
            TypesFactory.instance() if types_factory is None else types_factory
        )
        self._parameters = self.initialize_parameters()

    def initialize_parameters(self) -> Parameters:
        """Parse the parameters if present.

        They only need to be parsed once.

        Returns:
            The parsed parameters.

        Example:

        .. code-block:: xml

            <prodid>
                <text>-//Example Inc.//Example Client//EN</text>
            </prodid>
        """
        element = self.parse_optional_tag("parameters")
        if element is None:
            return Parameters()
        parameters_parser = XCalParametersParser(element, self._types_factory)
        return parameters_parser.parse_parameters()

    def parse_parameters(self) -> Parameters:
        """Return the parsed parameters."""
        return self._parameters

    def parse_property(self):
        """Parse one property from the list.

        Example:

        .. code-block:: xml

            <prodid>
                <text>-//Example Inc.//Example Client//EN</text>
            </prodid>
        """
        start = self._consumed
        value_type = self._types_factory.for_property(self.tag, self.child.tag)
        result = value_type.from_xcal(self)
        if self._consumed == start:
            raise InvalidParserState(
                f"Endless loop detected: {value_type} did not consume any XML."
            )
        return result
