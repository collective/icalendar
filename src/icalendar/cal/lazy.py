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


class BigCalendar(Calendar):
    """A calendar that can handle big files.

    Subcomponents of this calendar are evaluated lazily,
    meaning that they are not parsed until they are accessed.
    This allows the calendar to handle large files without consuming too much memory.

    All the properties of the calendar are parsed immediately,
    just the subcomponents are not.
    """

    _subcomponents: list[Component]

    def __init__(self, *args, **kwargs):
        """Initialize the calendar."""
        super().__init__(*args, **kwargs)
        self._lazy_subcomponents: list[LazySubcomponent] | None = []

    @property
    def subcomponents(self) -> list[Component]:
        """The subcomponents of the calendar.

        Parse all subcomponents of the calendar and return them as a list.
        """
        self.parse_initial_components()
        if not self._subcomponents:
            self._subcomponents = [
                lazy_subcomponent.parse()
                for lazy_subcomponent in self._lazy_subcomponents
            ]
        return self._subcomponents

    @subcomponents.setter
    def subcomponents(self, value: list[Component]) -> None:
        """Set the subcomponents of the calendar."""
        self._subcomponents = value

    def parse_initial_components(self):
        """Parse the components that are required by other components.

        This mainly concerns the timezone components.
        They are required by other components that have a TZID parameter.
        """
        for component in self._lazy_subcomponents:
            if component.name == "VTIMEZONE":
                component.parse()

    # TODO: test setter

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


__all__ = ["BigCalendar"]
