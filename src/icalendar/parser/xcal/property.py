from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import XCalParser
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
        self._component[self.child.tag] = values
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
        self._parameters = self.parse_parameters()

    def parse_parameters(self) -> Parameters:
        """Parse the parameters if present.

        Returns:
            The parsed parameters.

        Example:

        .. code-block:: xml

            <prodid>
                <text>-//Example Inc.//Example Client//EN</text>
            </prodid>
        """
        params = Parameters()
        if self.is_finished() or self.child.tag != "parameters":
            return params
        parameters_parser = XCalParametersParser(
            self.child, params, self._types_factory
        )
        parameters_parser.parse_parameters()
        self.done()
        return params

    def parse_property(self):
        """Parse one property from the list.

        Example:

        .. code-block:: xml

            <prodid>
                <text>-//Example Inc.//Example Client//EN</text>
            </prodid>
        """
