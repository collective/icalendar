"""A parser for components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.error import InvalidToken, XCalParsingError
from icalendar.parser.xcal.adapter import ElementAdapter
from icalendar.parser.xcal.base import XCalParser
from icalendar.parser.xcal.property import XCalPropertiesParser
from icalendar.timezone import tzp

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.cal.component import Component
    from icalendar.cal.component_factory import ComponentFactory
    from icalendar.prop.factory import TypesFactory


class XCalComponentParser(XCalParser):
    """A parser for components.

    Parameters:
        component_factory: The component factory to use.
        element: The element to parse.
        types_factory: The types factory to use.

    Examples:

        The ``element`` can be a an ``icalendar`` stream that contains
        one or more ``vcalendar`` components.

        .. code-block:: xml

            <icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
              <vcalendar>
                ...
              </vcalendar>
            </icalendar>

        Components can contain other components inside the ``components`` tag.
        The parameter ``element`` can be such a ``components`` tag.

        .. code-block:: xml

            <components>
              <vevent>
                ...
              </vevent>
            </components>

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
        """Convert one child into a :class:`~icalendar.cal.component.Component`.

        Returns:
            The parsed component.

        Raises:
            ~icalendar.error.XCalParsingError: If there is an error in the child.
            ~icalendar.parser.xcal.base.InvalidParserState:
                If all components have been parsed or a property value type did not
                parse anything.

        Example:

            The XML below shows the structure of one component
            element that gets parsed by this method.
            ``vcalendar`` is the name of the component.
            Each component can contain a ``properties`` and
            a ``components`` element with more components.

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
            The parsed component.

        Raises:
            ~icalendar.error.XCalParsingError: If there is an error in the child.
            ~icalendar.parser.xcal.base.InvalidParserState:
                If all components have been parsed or a property value type did not
                parse anything.

        """
        return self._parse_component(self.child)

    def _parse_component(self, element: ElementAdapter) -> Component:
        """Parse a component, completing timezone children before their siblings."""
        try:
            component_class = self._component_factory.get_component_class(element.tag)
        except InvalidToken as error:
            raise XCalParsingError(
                "The component name must be a valid iCalendar token",
                element.tag,
                element,
            ) from error
        component = component_class()
        properties = element.get_child_with_tag("properties")
        if properties is not None:
            properties_parser = XCalPropertiesParser(
                properties, component, self._types_factory
            )
            properties_parser.parse_properties()
        components = element.get_child_with_tag("components")
        if components is not None:
            children = components.children
            parsed = {}
            for i in sorted(
                range(len(children)), key=lambda i: children[i].tag != "vtimezone"
            ):
                parsed[i] = self._parse_component(children[i])
            for i in range(len(children)):
                component.add_component(parsed[i])
        if component.name == "VTIMEZONE" and "TZID" in component:
            tzp.cache_timezone_component(component)
        return component


__all__ = ["XCalComponentParser"]
