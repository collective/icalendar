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

    def get_all_components(self) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
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

    def walk(self, name: str) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given name."""
        result = []
        for component in self._components:
            result += component.walk(name)
        return self, result

    def with_uid(
        self, name: str
    ) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given uid."""
        result = []
        for component in self._components:
            result += component.with_uid(name)
        return self, result


class LazySubcomponentsStrategy:
    """All the subcomponents are parsed lazily."""

    initial_components_to_parse: tuple[str, ...] = ("VTIMEZONE",)
    """The components that are parsed immediately, instead of lazily."""

    def __init__(self):
        self._components: list[LazySubcomponent | Component] = []
        self._initial_parsed: bool = False

    @property
    def as_parsed(self) -> ParsedSubcomponentsStrategy:
        """The same components just fully parsed."""
        return ParsedSubcomponentsStrategy().set_components(
            [component.parse() for component in self._components]
        )

    def get_all_components(self) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar.

        Parse all subcomponents.
        """
        self.parse_initial_components()
        return self.as_parsed.get_all_components()

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
        if self._initial_parsed:
            return
        self._initial_parsed = True
        for component in self._components:
            if component.name in self.initial_components_to_parse:
                component.parse()

    def walk(
        self, name: str | None
    ) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given name.

        Parse only the minumal number of subcomponents.
        """
        if name is None:
            return self.as_parsed.walk(name)
        self.parse_initial_components()
        result = []
        for component in self._components:
            result += component.walk(name)
        return self, result

    def with_uid(self, uid: str) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given uid.

        Parse only the minumal number of subcomponents.
        """
        self.parse_initial_components()
        result = []
        for component in self._components:
            result += component.with_uid(uid)
        return self, result


class InitialSubcomponentsStrategy:
    def set_components(self, components: list[Component]) -> LazySubcomponentsStrategy:
        """Set the subcomponents of the calendar."""
        assert components == []
        return LazySubcomponentsStrategy()


class LazyCalendar(Calendar):
    """A calendar that can handle big files.

    Subcomponents of this calendar are evaluated lazily,
    meaning that they are not parsed until they are accessed.
    This allows the calendar to handle large files without
    consuming too much memory or time.

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
        self._subcomponents, result = self._subcomponents.get_all_components()
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
        """Whether the subcomponents will be parsed lazily.

        Returns:
            False if all subcomponents are parsed.
            True if subcomponents are parsed before they get accessed.
        """
        return self._subcomponents.is_lazy()

    def _walk(
        self, name: str | None, select: callable[[Component], bool]
    ) -> list[Component]:
        self._subcomponents, result = self._subcomponents.walk(name)
        result = [component for component in result if select(component)]
        if (name is None or self.name == name) and select(self):
            result.insert(0, self)
        return result

    def with_uid(self, uid: str) -> list[Component]:
        self._subcomponents, result = self._subcomponents.with_uid(uid)
        if self.uid == uid:
            result.insert(0, self)
        return result

    with_uid.__doc__ = Calendar.with_uid.__doc__


__all__ = ["LazyCalendar"]
