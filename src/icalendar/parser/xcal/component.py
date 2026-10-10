"""A parser for components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.xcal.adapter import ElementAdapter
from icalendar.parser.xcal.base import XCalParser
from icalendar.parser.xcal.property import XCalPropertiesParser

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.cal.component import Component
    from icalendar.cal.component_factory import ComponentFactory
    from icalendar.prop.factory import TypesFactory


class XCalComponentParser(XCalParser):
    """A parser for components.

    Parameters:
        element: The element to parse.
        component_factory: The component factory to use.
        types_factory: The types factory to use.
    """

    def __init__(
        self,
        element: Element | ElementAdapter,
        component_factory: ComponentFactory,
        types_factory: TypesFactory,
    ) -> None:
        element = ElementAdapter.with_element(element)
        if element.tag not in ("icalendar", "components"):
            # we are not in an icalendar/component stream. We need to wrap it.
            # This only happens when you pass in a single component.
            element = element.make_parent("icalendar")
        super().__init__(element)
        self._component_factory = component_factory
        self._types_factory = types_factory

    def parse_component(self) -> Component:
        """Consume one child as a component.

        Returns:
            The consumed component.

        Raises:
            ~icalendar.error.XCalParsingError: If there is an error in the child
            ~icalendar.parser.xcal.base.InvalidParserState:
                If all components have been parsed or a property value type did not
                parse anything.

        Example:

            .. code-block:: xml

                <vcalendar>
                  <properties>
                    ...
                  </properties>
                  <components>
                    <vevent>
                    ...
                    </vevent>
                  </components>
                </vcalendar>
        """
        component = self.parse_component_from_child()
        self.done()
        return component

    def parse_component_from_child(self) -> Component:
        """Parse a component from a child element.

        Returns:
            The parsed component

        Raises:
            ~icalendar.error.XCalParsingError: If there is an error in the child
            ~icalendar.parser.xcal.base.InvalidParserState:
                If all components have been parsed or a property value type did not
                parse anything.

        """
        component_class = self._component_factory.get_component_class(self.child.tag)
        component = component_class()
        properties = self.child.get_child_with_tag("properties")
        if properties is not None:
            properties_parser = XCalPropertiesParser(
                properties, component, self._types_factory
            )
            properties_parser.parse_properties()
        components = self.child.get_child_with_tag("components")
        if components is not None:
            components_parser = XCalComponentParser(
                components, self._component_factory, self._types_factory
            )
            while not components_parser.is_finished():
                component.add_component(components_parser.parse_component())
        return component


__all__ = ["XCalComponentParser"]
