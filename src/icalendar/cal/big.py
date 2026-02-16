"""Pasing big calendar files."""

from __future__ import annotations

from .calendar import Calendar


class BigCalendar(Calendar):
    """A calendar that can handle big files.

    Subcomponents of this calendar are evaluated lazily,
    meaning that they are not parsed until they are accessed.
    This allows the calendar to handle large files without consuming too much memory.

    All the properties of the calendar are parsed immediately,
    just the subcomponents are not.
    """


__all__ = ["BigCalendar"]
