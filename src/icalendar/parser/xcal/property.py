from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.error import XCalParsingError
from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import InvalidParserState, XCalParser
from icalendar.parser.xcal.parameters import XCalParameterParser, XCalParametersParser
from icalendar.prop.broken import vBroken
from icalendar.prop.empty import vEmtpy
from icalendar.prop.unknown import vUnknown

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.cal.component import Component
    from icalendar.parser.xcal.adapter import ElementAdapter
    from icalendar.prop import VPROPERTY
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
        if not values:
            # We have an empty property
            parameters = property_parser.parse_parameters()
            if parameters:
                # If there are parameters, it is worth remembering them
                values = [vEmtpy.from_xcal(property_parser)]
        if values:
            previous = self._component.get(self.child.tag)
            if previous is None:
                # first occurrence of the parameter
                self._component[self.child.tag] = (
                    values[0] if len(values) == 1 else values
                )
            # the parameter occurs several times
            elif not isinstance(previous, list):
                # one value previously
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

    def parse_property(self) -> VPROPERTY:
        """Parse one property from the list.

        Returns:
            The parsed property

        Raises:
            InvalidParserState: If no parsing takes place.

        Example:

        .. code-block:: xml

            <prodid>
                <text>-//Example Inc.//Example Client//EN</text>
            </prodid>

        """
        start = self._consumed
        child = self.child
        property_name = self.tag
        value_parameter = child.tag
        value_type = self._types_factory.for_property(property_name, value_parameter)
        try:
            result = value_type.from_xcal(self)
        except XCalParsingError as e:
            if self._consumed == start:
                result = vUnknown.from_first_xcal_element(self)
            else:
                result = vBroken.from_parse_error(
                    child.get_inner_text(),
                    Parameters(),
                    property_name.upper(),
                    value_type.__name__,
                    e,
                )
            # if self._consumed == start:
            #     # if we did not progress, we should move on
            #     self.done()
        else:
            expected_type = self._types_factory.types_map.get(property_name, None)
            if (
                expected_type is not None
                and expected_type.lower() == value_parameter.lower()
            ):
                # We delete the VALUE parameter if this is the default value.
                result.params.value = None
            if isinstance(result, vBroken):
                # We can get an x-broken property that we created ourselves.
                # In this case, we set additional attributes.
                result.property_name = property_name.upper()
                result.expected_type = self._types_factory.for_property(
                    property_name
                ).__name__
                result.parse_error = XCalParsingError(
                    f"Could not parse {result.property_name}"
                    f" with {result.expected_type}",
                    None,  # avoid recursion
                    child,
                )
        if self._consumed == start:
            raise InvalidParserState(
                f"Endless loop detected: {value_type} did not consume any XML."
            )
        return result
