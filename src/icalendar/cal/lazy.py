"""Components for lazy parsing of components."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from icalendar.cal.component_factory import ComponentFactory
from icalendar.parser.ical.lazy import LazyCalendarIcalParser

from .calendar import Calendar

if TYPE_CHECKING:
    from collections.abc import Callable

    from icalendar.cal import Component
    from icalendar.parser.ical.component import ComponentIcalParser
    from icalendar.parser.ical.lazy import LazySubcomponent


class ParsedSubcomponentsStrategy:
    """All the subcomponents are parsed and available as a list."""

    def __init__(self) -> None:
        self._components: list[Component] = []

    def get_all_components(self) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the parsed subcomponents of the calendar.

        Returns:
            A tuple of this strategy and the list of parsed subcomponents.
        """
        return self, self._components

    def set_components(
        self, components: list[Component]
    ) -> ParsedSubcomponentsStrategy:
        """Set the subcomponents of the calendar.

        Parameters:
            components: The parsed subcomponents to store.

        Returns:
            This strategy with the subcomponents stored.
        """
        self._components = components
        return self

    def add_component(self, component: Component) -> ParsedSubcomponentsStrategy:
        """Add a component to the calendar, parsing it immediately.

        Parameters:
            component: The component to add.

        Returns:
            This strategy with the component added.
        """
        self._components.append(component.parse())
        return self

    def is_lazy(self) -> Literal[False]:
        """Return ``False`` because subcomponents are not lazily parsed."""
        return False

    def walk(self, name: str) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given name.

        Parameters:
            name: The component name to filter by, for example, ``"VEVENT"``.

        Returns:
            A tuple of this strategy and the matching subcomponents.
        """
        result = []
        for component in self._components:
            result += component.walk(name)
        return self, result

    def with_uid(
        self, name: str
    ) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given UID.

        Parameters:
            name: The UID to search for.

        Returns:
            A tuple of this strategy and the matching subcomponents.
        """
        result = []
        for component in self._components:
            result += component.with_uid(name)
        return self, result


class LazySubcomponentsStrategy:
    """Parse subcomponents only when accessed."""

    initial_components_to_parse: tuple[str, ...] = ("VTIMEZONE",)
    """Parse these subcomponents before any others."""

    def __init__(self) -> None:
        self._components: list[LazySubcomponent | Component] = []
        self._initial_parsed: bool = False

    @property
    def as_parsed(self) -> ParsedSubcomponentsStrategy:
        """Return a parsed strategy with all subcomponents parsed.

        Returns:
            A :class:`ParsedSubcomponentsStrategy` with all subcomponents.
        """
        return ParsedSubcomponentsStrategy().set_components(
            [component.parse() for component in self._components]
        )

    def get_all_components(self) -> tuple[ParsedSubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar, parsing all of them.

        Returns:
            A tuple of a parsed strategy and the list of subcomponents.
        """
        self.parse_initial_components()
        return self.as_parsed.get_all_components()

    def set_components(
        self, components: list[Component]
    ) -> ParsedSubcomponentsStrategy:
        """Set the subcomponents of the calendar.

        Parameters:
            components: The subcomponents to store.

        Returns:
            A :class:`ParsedSubcomponentsStrategy` holding the components.
        """
        return ParsedSubcomponentsStrategy().set_components(components)

    def add_component(
        self, component: Component | LazySubcomponent
    ) -> LazySubcomponentsStrategy:
        """Add a component to the calendar without parsing it.

        Parameters:
            component: The component to add.

        Returns:
            This strategy with the component added.
        """
        self._components.append(component)
        return self

    def is_lazy(self) -> bool:
        """Return whether the subcomponents may be lazily parsed."""
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
    ) -> tuple[LazySubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given name.

        Parse only the minimal number of subcomponents.

        Parameters:
            name: The component name to filter by, or ``None`` for all.

        Returns:
            A tuple of this strategy and the matching subcomponents.
        """
        if name is None:
            return self.as_parsed.walk(name)
        self.parse_initial_components()
        result = []
        for component in self._components:
            result += component.walk(name)
        return self, result

    def with_uid(self, uid: str) -> tuple[LazySubcomponentsStrategy, list[Component]]:
        """Get the subcomponents of the calendar with the given ``uid``.

        Parse only the minimal number of subcomponents.

        Parameters:
            uid: The UID to search for.

        Returns:
            A tuple of this strategy and the matching subcomponents.
        """
        self.parse_initial_components()
        result = []
        for component in self._components:
            result += component.with_uid(uid)
        return self, result


class InitialSubcomponentsStrategy:
    """Initial strategy for the calendar.

    No subcomponents.
    """

    def set_components(self, components: list[Component]) -> LazySubcomponentsStrategy:
        """Set the subcomponents, switching to lazy parsing.

        Parameters:
            components: The subcomponents to store. Must be empty for an
                uninitialised calendar.

        Raises:
            ValueError: If ``components`` is not empty. Parse the calendar
                first or use :meth:`LazyCalendar.add_component` instead.
        """
        if components:
            raise ValueError(
                "Cannot set subcomponents on an uninitialised LazyCalendar. "
                "Parse it first or add components via add_component()."
            )
        return LazySubcomponentsStrategy()


class LazyCalendar(Calendar):
    """A calendar that parses subcomponents lazily for memory efficiency.

    Subcomponents of this calendar are parsed only when accessed,
    allowing the calendar to handle large files without consuming
    too much memory or time. All calendar-level properties are parsed
    immediately; subcomponents and their properties are deferred.

    Examples:

        By accessing the :attr:`~icalendar.cal.calendar.Calendar.events` of the calendar,
        only :class:`~icalendar.cal.event.Event` and
        :class:`~icalendar.cal.timezone.Timezone` are immediately parsed.

        .. code-block:: pycon

            >>> from icalendar import LazyCalendar
            >>> calendar = LazyCalendar.example("issue_1050_all_components")
            >>> len(calendar.events) == 1
            True

        The calendar's subcomponents were not parsed because they were not accessed.
        The calendar is still lazy.

            >>> calendar.is_lazy()
            True

        When you access all :attr:`~icalendar.cal.component.Component.subcomponents` of the calendar,
        for example by getting their count, the entire calendar is
        parsed and becomes not lazy.

            >>> len(calendar.subcomponents)
            5
            >>> calendar.is_lazy()
            False

    See also:
        :meth:`ComponentIcalParser.parse <icalendar.parser.ical.component.ComponentIcalParser.parse>`
    """

    _subcomponents: (
        LazySubcomponentsStrategy
        | ParsedSubcomponentsStrategy
        | InitialSubcomponentsStrategy
    )
    """The strategy pattern for subcomponents of the calendar."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the calendar."""
        self._subcomponents = InitialSubcomponentsStrategy()
        super().__init__(*args, **kwargs)

    @property
    def subcomponents(self) -> list[Component]:
        """Parse and return all subcomponents of this calendar.

        Accessing this property triggers the parsing of all deferred
        subcomponents. Once accessed, the calendar is no longer lazy.

        You can manipulate the returned list or set it to replace all
        subcomponents. Setting the list does not re-enable lazy parsing.

        Returns:
            A list of parsed subcomponents.

        See also:
            -   :attr:`~icalendar.cal.component.Component.subcomponents`
            -   :meth:`is_lazy`

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
        """Add a component to this calendar.

        This adds a subcomponent without parsing the entire calendar.
        Use this, instead of appending to
        :attr:`~icalendar.cal.lazy.LazyCalendar.subcomponents`
        which forces all subcomponents to be parsed first.

        Parameters:
            component: The component to add as a subcomponent.

        See also:
            :meth:`Component.add_component <icalendar.cal.component.Component.add_component>`
        """
        self._subcomponents = self._subcomponents.add_component(component)

    def is_lazy(self) -> bool:
        """Whether the subcomponents are still deferred and not yet parsed.

        Returns ``True`` if subcomponents have not been accessed yet.
        Returns ``False`` once all subcomponents have been parsed,
        for example, by accessing :attr:`subcomponents`.

        .. note:: If you believe the calendar parses more subcomponents than
            it should, please `open an issue
            <https://github.com/collective/icalendar/issues/new?template=bug_report.md>`_.

        Returns:
            ``True`` if subcomponent parsing is deferred.
            ``False`` if all subcomponents have been parsed.
        """
        return self._subcomponents.is_lazy()

    def _walk(
        self, name: str | None, select: Callable[[Component], bool]
    ) -> list[Component]:
        self._subcomponents, result = self._subcomponents.walk(name)
        result = [component for component in result if select(component)]
        if (name is None or self.name == name) and select(self):
            result.insert(0, self)
        return result

    def with_uid(self, uid: str) -> list[Component]:
        """Return subcomponents matching the given UID without parsing all subcomponents.

        This searches lazily, parsing only the minimal subcomponents
        needed to find matches. If this calendar's own UID matches,
        it is included as the first element.

        Parameters:
            uid: The UID to search for.

        Returns:
            A list of components whose UID matches, with the calendar itself
            first if it matches.

        See also:
            :meth:`Component.with_uid <icalendar.cal.component.Component.with_uid>`
        """
        self._subcomponents, result = self._subcomponents.with_uid(uid)
        if self.uid == uid:
            result.insert(0, self)
        return result


__all__ = ["LazyCalendar"]

if __name__ == "__main__":
    import timeit

    calendar = Calendar.example("issue_1050_all_components")
    COUNT = 10000
    calendar.subcomponents *= COUNT
    ics = calendar.to_ical()

    def _benchmark(cal: type[Calendar]):
        """Check out how fast this is."""
        cal = cal.from_ical(ics)
        assert len(cal.events) == COUNT

    for cal in [Calendar, LazyCalendar]:
        print("Benchmarking:", cal.__name__)  # noqa: T201
        print(timeit.timeit("_benchmark(cal)", globals=locals(), number=1))  # noqa: T201

    # Benchmarking: Calendar
    # 12.277852076000272
    # Benchmarking: LazyCalendar
    # 5.738950790999297
