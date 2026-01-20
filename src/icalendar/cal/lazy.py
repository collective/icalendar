"""Lazy subcomponent parsing for large calendars.

See `Issue #1050 <https://github.com/collective/icalendar/issues/1050>`_.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from icalendar.cal.calendar import Calendar
from icalendar.cal.component import Component
from icalendar.parser import Contentline, Contentlines
from icalendar.timezone import tzp

if TYPE_CHECKING:
    from icalendar.cal.availability import Availability
    from icalendar.cal.event import Event
    from icalendar.cal.free_busy import FreeBusy
    from icalendar.cal.journal import Journal
    from icalendar.cal.todo import Todo


class LazyCalendar(Calendar):
    """A :class:`~icalendar.cal.calendar.Calendar` with lazy subcomponent parsing for large files.

    Parses :class:`~icalendar.cal.calendar.Calendar` properties and VTIMEZONE components eagerly, but
    defers parsing of VEVENT, VTODO, VJOURNAL, VFREEBUSY, and VAVAILABILITY
    until accessed via ``.events``, ``.todos``, ``.walk()``, or other component
    methods.

    This is useful for:

    - Accessing calendar metadata without parsing all events
    - Counting events without full parsing overhead
    - Working with very large calendars (1000+ events)

    Example::

        from icalendar import LazyCalendar

        # Parse a large calendar file
        with open("large_calendar.ics", "rb") as f:
            cal = LazyCalendar.from_ical(f.read())

        # Access metadata immediately (no event parsing)
        cal["VERSION"]  # Returns vText('2.0')

        # Events are parsed on first access
        len(cal.events)  # Returns 1500

    .. note::
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
            LazyCalendar or list of LazyCalendar instances.
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

        Reuses the property parsing logic from Component.from_ical.
        """
        from icalendar.parser import Parameters, split_on_unescaped_comma

        uname = name.upper()
        value_param = params.get("VALUE") if params else None
        factory = cls.types_factory.for_property(name, value_param)

        datetime_names = ("DTSTART", "DTEND", "RECURRENCE-ID", "DUE", "RDATE", "EXDATE")
        tzid = params.get("TZID") if params and name in datetime_names else None

        # Handle CATEGORIES specially
        if uname == "CATEGORIES":
            line_str = str(line)
            colon_idx = line_str.rfind(":")
            if colon_idx > 0:
                raw_value = line_str[colon_idx + 1 :]
                try:
                    category_list = split_on_unescaped_comma(raw_value)
                    vals_inst = factory(category_list)
                    vals_inst.params = params
                    cal.add(name, vals_inst, encode=0)
                except ValueError:
                    # Invalid CATEGORIES value, skip property
                    pass
                return

        # Normal property parsing
        try:
            if tzid:
                parsed_val = factory.from_ical(vals, tzid)
            else:
                parsed_val = factory.from_ical(vals)
            vals_inst = factory(parsed_val)
            vals_inst.params = params if params else Parameters()
            cal.add(name, vals_inst, encode=0)
        except Exception:
            # Calendar is strict, so we should raise, but for robustness
            # just add as text if it fails
            pass

    def _parse_raw_component(self, index: int) -> Component:
        """Parse a raw component by index and add to subcomponents.

        If the component at the given index has already been parsed,
        returns the previously parsed component from subcomponents.

        Parameters:
            index: Index into self._raw_components.

        Returns:
            The parsed Component object.
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
        """Parse all raw components of a given type."""
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
            self._parse_all_of_type(name.upper())
        else:
            self._parse_all_raw()
        return super().walk(name, select)

    @property
    def events(self) -> list[Event]:
        """All :class:`~icalendar.cal.event.Event`\\ s in the calendar.

        :class:`~icalendar.cal.event.Event`\\ s are parsed on first access.
        """
        self._parse_all_of_type("VEVENT")
        return super().events

    @property
    def todos(self) -> list[Todo]:
        """All :class:`~icalendar.cal.todo.Todo`\\ s in the calendar.

        :class:`~icalendar.cal.todo.Todo`\\ s are parsed on first access.
        """
        self._parse_all_of_type("VTODO")
        return super().todos

    @property
    def journals(self) -> list[Journal]:
        """All :class:`~icalendar.cal.journal.Journal`\\ s in the calendar.

        :class:`~icalendar.cal.journal.Journal`\\ s are parsed on first access.
        """
        self._parse_all_of_type("VJOURNAL")
        return super().walk("VJOURNAL")

    @property
    def freebusy(self) -> list[FreeBusy]:
        """All :class:`~icalendar.cal.free_busy.FreeBusy` components in the calendar.

        :class:`~icalendar.cal.free_busy.FreeBusy` components are parsed on first access.
        """
        self._parse_all_of_type("VFREEBUSY")
        return super().freebusy

    @property
    def availabilities(self) -> list[Availability]:
        """All :class:`~icalendar.cal.availability.Availability` components in the calendar.

        :class:`~icalendar.cal.availability.Availability` components are parsed on first access.
        """
        self._parse_all_of_type("VAVAILABILITY")
        return super().availabilities

    def property_items(
        self, recursive: bool = True, sorted: bool = True
    ) -> list[tuple[str, Any]]:
        """Returns properties in this component and subcomponents.

        For unparsed components, reconstructs from stored raw lines
        to ensure correct round-trip serialization.

        Parameters:
            recursive: Include subcomponents.
            sorted: Sort property names.

        Returns:
            List of (name, value) tuples.
        """
        v_text = self.types_factory["text"]
        properties = [("BEGIN", v_text(self.name).to_ical())]

        # Calendar's own properties
        property_names = self.sorted_keys() if sorted else self.keys()
        for name in property_names:
            values = self[name]
            if isinstance(values, list):
                for value in values:
                    properties.append((name, value))
            else:
                properties.append((name, values))

        if recursive:
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

        properties.append(("END", v_text(self.name).to_ical()))
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
