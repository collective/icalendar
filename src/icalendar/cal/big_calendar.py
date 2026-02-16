"""Pasing big calendar files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .calendar import Calendar

if TYPE_CHECKING:
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


__all__ = ["BigCalendar"]
