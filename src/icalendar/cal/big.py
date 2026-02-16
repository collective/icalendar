"""Pasing big calendar files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .calendar import Calendar

if TYPE_CHECKING:
    from .component import Component


class BigCalendar(Calendar):
    """A calendar that can handle big files.

    Subcomponents of this calendar are evaluated lazily,
    meaning that they are not parsed until they are accessed.
    This allows the calendar to handle large files without consuming too much memory.

    All the properties of the calendar are parsed immediately,
    just the subcomponents are not.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the calendar."""
        super().__init__(*args, **kwargs)
        self._subcomponents: list[LazySubcomponent] = []

    @property
    def subcomponents(self) -> list[Component]:
        """The subcomponents of the calendar.

        Parse all subcomponents of the calendar and return them as a list.
        """

    def _walk(self, name, select):
        """Walk along the subcomponents of the calendar.

        Only the subcomponents that match the given name are parsed.
        If the name is None, all subcomponents are parsed.
        """
        return super()._walk(name, select)


class LazySubcomponent:
    """A subcomponent that is evaluated lazily.

    This class is used to represent a subcomponent of a calendar that is not parsed until it is accessed.
    """

    def __init__(self, data: bytes, parser: type[Component]):
        """Initialize the lazy subcomponent with the raw data."""
        self._data = data
        self._parser = parser
        self._component: Component | None = None

    def parse(self) -> Component:
        """Parse the raw data and return the component."""
        if self._component is None:
            self._component = self._parser.from_ical(self._data)
        return self._component


__all__ = ["BigCalendar"]
