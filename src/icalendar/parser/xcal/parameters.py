from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import InvalidParserState, XCalParser

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.parser.xcal.adapter import ElementAdapter
    from icalendar.prop import VPROPERTY
    from icalendar.prop.factory import TypesFactory


class XCalParametersParser(XCalParser):
    """A parser for <properties>."""

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
        self._parameters = Parameters()

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

    def parse_parameter(self) -> VPROPERTY:
        """Parse one parameter value if present.

        Returns:
            The parsed parameters.

        Example:

        .. code-block:: xml

            <tzid>
                <text>US/Eastern</text>
            </tzid>
        """
        start = self._consumed
        value_type = self._types_factory.for_property(self.tag, self.child.tag)
        result = value_type.from_xcal(self)
        if self._consumed == start:
            raise InvalidParserState(
                f"Endless loop detected: {value_type} did not consume any XML."
            )
        return result
