"""Components for lazy parsing of components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.cal.component_factory import ComponentFactory
from icalendar.parser.ical.lazy import LazyCalendarIcalParser

from .calendar import Calendar

if TYPE_CHECKING:
    from icalendar.parser.ical.component import ComponentIcalParser
    from icalendar.parser.ical.lazy import LazySubcomponent

    from .component import Component


class ParsedSubcomponentsStrategy:
    """All the subcomponents are parsed and available as a list."""

    def __init__(self):
        self._components: list[Component] = []

    def get_components(self) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar."""
        return self, self._components

    def set_components(
        self, components: list[Component]
    ) -> ParsedSubcomponentsStrategy:
        """Set the subcomponents of the calendar."""
        self._components = components
        return self

    def add_component(self, component: Component) -> ParsedSubcomponentsStrategy:
        """Add a component to the calendar."""
        self._components.append(component.parse())
        return self

    def is_lazy(self) -> bool:
        """Return whether the components are lazy."""
        return False


class LazySubcomponentsStrategy:
    """All the subcomponents are parsed lazily."""

    initial_components_to_parse: tuple[str, ...] = ("VTIMEZONE",)
    """The components that are parsed immediately, instead of lazily."""

    def __init__(self):
        self._components: list[LazySubcomponent] = []

    def get_components(self) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar.

        Parse all subcomponents of the calendar and return them as a list.
        """
        new_strategy = ParsedSubcomponentsStrategy().set_components(
            [component.parse() for component in self._components]
        )
        return new_strategy.get_components()

    def set_components(
        self, components: list[Component]
    ) -> ParsedSubcomponentsStrategy:
        """Set the subcomponents of the calendar."""
        return ParsedSubcomponentsStrategy().set_components(components)

    def add_component(
        self, component: Component | LazySubcomponent
    ) -> LazyCalendarIcalParser:
        """Add a component to the calendar."""
        self._components.append(component)
        return self

    def is_lazy(self) -> bool:
        """Return whether the components are lazy."""
        return True

    def parse_initial_components(self) -> None:
        """Parse the components that are required by other components.

        This mainly concerns the timezone components.
        They are required by other components that have a TZID parameter.
        """
        for component in self._components:
            if component.name in self.initial_components_to_parse:
                component.parse()


class InitialSubcomponentsStrategy:
    def set_components(self, components: list[Component]) -> LazySubcomponentsStrategy:
        """Set the subcomponents of the calendar."""
        assert components == []
        return LazySubcomponentsStrategy()


class BigCalendar(Calendar):
    """A calendar that can handle big files.

    Subcomponents of this calendar are evaluated lazily,
    meaning that they are not parsed until they are accessed.
    This allows the calendar to handle large files without consuming too much memory.

    All the properties of the calendar are parsed immediately,
    just the subcomponents are not.
    """

    _subcomponents: (
        LazySubcomponentsStrategy
        | ParsedSubcomponentsStrategy
        | InitialSubcomponentsStrategy
    )
    """The stategy pattern for subcomponents of the calendar."""

    def __init__(self, *args, **kwargs):
        """Initialize the calendar."""
        self._subcomponents = InitialSubcomponentsStrategy()
        super().__init__(*args, **kwargs)

    @property
    def subcomponents(self) -> list[Component]:
        """The subcomponents of the calendar.

        Parse all subcomponents of the calendar and return them as a list.
        """
        self._subcomponents, result = self._subcomponents.get_components()
        return result

    @subcomponents.setter
    def subcomponents(self, value: list[Component]) -> None:
        """Set the subcomponents of the calendar."""
        self._subcomponents = self._subcomponents.set_components(value)

    @classmethod
    def _get_ical_parser(cls, st: str | bytes) -> ComponentIcalParser:
        """Get the iCal parser for the given input string."""
        return LazyCalendarIcalParser(
            st, cls._get_component_factory(), cls.types_factory
        )

    @classmethod
    def _get_component_factory(cls) -> ComponentFactory:
        """Get the component factory for this calendar."""
        factory = ComponentFactory()
        factory.add_component_class(cls)
        return factory

    def add_component(self, component: Component) -> None:
        """Add a component to the calendar."""
        self._subcomponents = self._subcomponents.add_component(component)

    def is_lazy(self):
        """Wether subcomponents will be evaluated lazily."""
        return self._subcomponents.is_lazy()


__all__ = ["BigCalendar"]
