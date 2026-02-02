"""Lazy subcomponent parsing for large calendars.

See issue :issue:`1050`.
"""

from __future__ import annotations

from typing import Any, ClassVar

from icalendar.cal.calendar import Calendar
from icalendar.cal.component import Component
from icalendar.parser import Contentline, Contentlines
from icalendar.timezone import tzp


class LazyCalendar(Calendar):
    """A :class:`~icalendar.cal.calendar.Calendar` with lazy subcomponent parsing for large files.

    Parses :class:`~icalendar.cal.calendar.Calendar` properties and VTIMEZONE components eagerly, but
    defers parsing of VEVENT, VTODO, VJOURNAL, VFREEBUSY, and VAVAILABILITY
    until accessed via :attr:`~icalendar.cal.calendar.Calendar.events`,
    :attr:`~icalendar.cal.calendar.Calendar.todos`,
    :meth:`~icalendar.cal.component.Component.walk`, or other component methods.

    This is useful for:

    - Accessing calendar metadata without parsing all events
    - Counting events without full parsing overhead
    - Working with very large calendars (1000+ events)

    Example:
        .. code-block:: py

            from icalendar import LazyCalendar

            # Parse a large calendar file
            with open("large_calendar.ics", "rb") as f:
                cal = LazyCalendar.from_ical(f.read())

            # Access metadata immediately (no event parsing)
            cal["VERSION"]  # Returns vText('2.0')

            # Events are parsed on first access
            len(cal.events)  # Returns 1500

    Note:
        Once accessed, components are fully parsed and cached.
        Subsequent accesses return the same parsed objects.

        The :meth:`~icalendar.cal.component.Component.to_ical` method produces correct output whether
        components have been parsed or not.
    """

    #: Components that should be parsed lazily.
    LAZY_COMPONENTS: ClassVar[frozenset[str]] = frozenset(
        {"VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY", "VAVAILABILITY"}
    )

    #: Components that must be parsed eagerly (needed for timezone resolution).
    EAGER_COMPONENTS: ClassVar[frozenset[str]] = frozenset({"VTIMEZONE"})

    # Marker for raw content lines in property_items() output
    _RAW_LINE_MARKER: ClassVar[str] = "_RAW_LINE"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store raw lines for unparsed components: list of (name, raw_lines)
        # raw_lines is a list of Contentline objects
        self._raw_components: list[tuple[str, list[Contentline]]] = []
        # Track which have been parsed (by index)
        self._parsed_indices: set[int] = set()

    @classmethod
    def from_ical(
        cls, st: bytes | str, multiple: bool = False
    ) -> LazyCalendar | list[LazyCalendar]:
        """Parse iCalendar data with lazy subcomponent parsing.

        :class:`~icalendar.cal.calendar.Calendar` properties and VTIMEZONE are parsed immediately.
        Other subcomponents—such as VEVENT or VTODO—are stored as raw
        content lines and parsed on first access.

        Parameters:
            st (bytes | str): iCalendar data as bytes or string.
            multiple (bool): If ``True``, returns list. If ``False``, returns
                single calendar.

        Returns:
            :class:`~icalendar.cal.lazy.LazyCalendar` or list of :class:`~icalendar.cal.lazy.LazyCalendar` instances.
        """
        calendars: list[LazyCalendar] = []
        lines = Contentlines.from_ical(st)

        line_index = 0
        while line_index < len(lines):
            line = lines[line_index]
            if not line:
                line_index += 1
                continue

            try:
                name, params, vals = line.parts()
            except ValueError:
                line_index += 1
                continue

            if name.upper() == "BEGIN" and vals.upper() == "VCALENDAR":
                cal = cls()
                line_index += 1

                # Parse until END:VCALENDAR
                while line_index < len(lines):
                    line = lines[line_index]
                    if not line:
                        line_index += 1
                        continue

                    try:
                        name, params, vals = line.parts()
                    except ValueError:
                        line_index += 1
                        continue

                    uname = name.upper()

                    if uname == "END" and vals.upper() == "VCALENDAR":
                        line_index += 1
                        break
                    if uname == "BEGIN":
                        component_name = vals.upper()
                        # Collect all lines for this component
                        start_idx = line_index
                        depth = 1
                        line_index += 1
                        while line_index < len(lines) and depth > 0:
                            line = lines[line_index]
                            if line:
                                try:
                                    n, _, v = line.parts()
                                    if n.upper() == "BEGIN":
                                        depth += 1
                                    elif n.upper() == "END":
                                        depth -= 1
                                except ValueError:
                                    # Malformed line while scanning BEGIN/END blocks
                                    pass
                            line_index += 1
                        end_idx = line_index

                        # Collect raw lines for this component
                        raw_lines = [
                            lines[j] for j in range(start_idx, end_idx) if lines[j]
                        ]

                        if component_name in cls.EAGER_COMPONENTS:
                            # Parse VTIMEZONE eagerly using existing Component.from_ical
                            raw_str = "\r\n".join(str(ln) for ln in raw_lines)
                            component = Component.from_ical(raw_str)
                            cal.add_component(component)
                            if component_name == "VTIMEZONE" and "TZID" in component:
                                tzp.cache_timezone_component(component)
                        elif component_name in cls.LAZY_COMPONENTS:
                            # Store raw for lazy parsing
                            cal._raw_components.append((component_name, raw_lines))
                        else:
                            # Unknown/custom components - also defer
                            cal._raw_components.append((component_name, raw_lines))
                    else:
                        # Calendar-level property - parse eagerly
                        cls._parse_calendar_property(cal, name, params, vals, line)
                        line_index += 1

                calendars.append(cal)
            else:
                line_index += 1

        if multiple:
            return calendars
        if len(calendars) > 1:
            raise ValueError(
                cls._format_error(
                    "Found multiple components where only one is allowed", st
                )
            )
        if len(calendars) < 1:
            raise ValueError(
                cls._format_error(
                    "Found no components where exactly one is required", st
                )
            )
        return calendars[0]

    @classmethod
    def _parse_calendar_property(cls, cal, name, params, vals, line):
        """Parse a single calendar-level property.

        Uses the shared property parsing logic from Component._parse_single_property.
        """
        cls._parse_single_property(cal, name, params, vals, line, ignore_errors=True)

    def _parse_raw_component(self, index: int) -> Component:
        """Parse a raw component by index and add to subcomponents.

        If the component at the given index has already been parsed,
        returns the previously parsed component from subcomponents.

        Parameters:
            index: Index into self._raw_components.

        Returns:
            The parsed :class:`~icalendar.cal.component.Component` object.
        """
        if index in self._parsed_indices:
            # Already parsed - find and return the component from subcomponents
            comp_name, _ = self._raw_components[index]
            for comp in self.subcomponents:
                if comp.name == comp_name:
                    return comp
            raise AssertionError(
                f"Parsed component {comp_name!r} at index {index} not in subcomponents"
            )

        comp_name, raw_lines = self._raw_components[index]
        raw_str = "\r\n".join(str(ln) for ln in raw_lines)
        component = Component.from_ical(raw_str)
        self.subcomponents.append(component)
        self._parsed_indices.add(index)
        return component

    def _parse_all_of_type(self, name: str) -> None:
        """Parse all raw components of a given type.

        Parameters:
            name: Component type name (case-insensitive, e.g., "VEVENT" or "vevent").
        """
        name = name.upper()
        for i, (comp_name, _raw_lines) in enumerate(self._raw_components):
            if i in self._parsed_indices:
                continue
            if comp_name == name:
                self._parse_raw_component(i)

    def _parse_all_raw(self) -> None:
        """Parse all remaining raw components."""
        for i in range(len(self._raw_components)):
            if i not in self._parsed_indices:
                self._parse_raw_component(i)

    def walk(self, name=None, select=lambda _: True) -> list[Component]:
        """Recursively traverse component and subcomponents.

        Parses lazy components as needed.

        Parameters:
            name: If provided, only return components with this name.
            select: Optional filter function.

        Returns:
            List of matching components.
        """
        if name is not None:
            self._parse_all_of_type(name)
        else:
            self._parse_all_raw()
        return super().walk(name, select)

    def _iter_property_items_subcomponents(
        self, sorted: bool = True
    ) -> list[tuple[str, Any]]:
        """Iterate over subcomponents for property_items().

        Overrides the base class to handle unparsed raw components,
        ensuring correct round-trip serialization without parsing.
        """
        properties = []
        # First: already-parsed subcomponents (includes VTIMEZONE)
        for subcomponent in self.subcomponents:
            properties += subcomponent.property_items(sorted=sorted)

        # Then: unparsed raw components
        for i, (_comp_name, raw_lines) in enumerate(self._raw_components):
            if i not in self._parsed_indices:
                # Output raw lines directly
                for raw_line in raw_lines:
                    # Use marker that content_line will handle
                    properties.append((self._RAW_LINE_MARKER, raw_line))

        return properties

    def content_line(self, name, value, sorted: bool = True):
        """Returns property as content line.

        Handles raw lines from unparsed components.
        """
        if name == self._RAW_LINE_MARKER:
            # Value is already a Contentline
            return value
        return super().content_line(name, value, sorted=sorted)


__all__ = ["LazyCalendar"]
