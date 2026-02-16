"""Parsing a component's ical data."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from icalendar.parser.content_line import Contentline, Contentlines
from icalendar.parser.property import split_on_unescaped_comma
from icalendar.prop import vBroken
from icalendar.timezone import tzp

if TYPE_CHECKING:
    from icalendar.cal import Component, ComponentFactory
    from icalendar.parser.parameter import Parameters
    from icalendar.prop import VPROPERTY, TypesFactory


class ComponentIcalParser:
    """A parser for a component's ical data.

    This uses the template method pattern,
    where the main parsing logic can be refined in the base class,
    """

    datetime_names: ClassVar[tuple[str, ...]] = (
        "DTSTART",
        "DTEND",
        "RECURRENCE-ID",
        "DUE",
        "RDATE",
        "EXDATE",
    )
    """Names to check for TZID parameter when parsing datetimes.

    Their from_ical methods take an optional tzid argument,
    which is used if the property has a TZID parameter.
    """

    def __init__(
        self,
        data: bytes | list[Contentline],
        component_factory: ComponentFactory,
        types_factory: TypesFactory,
    ):
        """Initialize the parser with the raw data.

        Parameters:
            data: The raw ical data to parse, as bytes or a list of content lines.
            component_factory: The factory to use for creating components.
            types_factory: The factory to use for creating property values.
        """
        self._data = data
        self._component_factory = component_factory
        self._types_factory = types_factory

    def initialize_parsing(self):
        self._stack = []
        self._components = []
        self._content_lines = (
            Contentlines.from_ical(self._data)
            if isinstance(self._data, bytes)
            else self._data
        )
        self._content_lines_iterator = iter(self._content_lines)
        self._tzp = tzp

    def handle_line_parse_error(self, exception: Exception):
        """Handle a line parsing error."""
        # if unable to parse a line within a component
        # that ignores exceptions, mark the component
        # as broken and skip the line. otherwise raise.
        component = self.component
        if not component or not component.ignore_exceptions:
            raise exception
        component.errors.append((None, str(exception)))

    def handle_begin_component(self, vals: str) -> None:
        """Handle the beginning of a component."""
        # try and create one of the components defined in the spec,
        # otherwise get a general Components for robustness.
        c_name = vals.upper()
        c_class = self._component_factory.get_component_class(c_name)
        # If component factory cannot resolve ``c_name``, the generic
        # ``Component`` class is used which does not have the name set.
        # That's opposed to the usage of ``cls``, which represents a
        # more concrete subclass with a name set (e.g. VCALENDAR).
        component = c_class()
        if not getattr(component, "name", ""):  # undefined components
            component.name = c_name
        self._stack.append(component)

    def handle_end_component(self, vals: str) -> None:
        """Handle the end of a component."""
        # we are done adding properties to this component
        # so pop it from the stack and add it to the new top.
        if not self._stack:
            # The stack is currently empty, the input must be invalid
            raise ValueError("END encountered without an accompanying BEGIN!")

        component = self._stack.pop()
        if not self._stack:  # we are at the end
            self._components.append(component)
        else:
            self._stack[-1].add_component(component)
        if vals == "VTIMEZONE" and "TZID" in component:
            tzp.cache_timezone_component(component)

    def prepare_components(self) -> None:
        """Prepare the parsed components.

        This is called when all components are parsed.
        """

    def parse(self) -> list[Component]:
        """Parse the raw data."""
        self.initialize_parsing()
        self.parse_content_lines()
        self.prepare_components()
        return self._components

    def parse_content_lines(self) -> None:
        """Parse the content lines."""
        for line in self._content_lines_iterator:  # raw parsing
            if not line:
                continue
            try:
                name, params, vals = line.parts()
            except ValueError as e:
                self.handle_line_parse_error(e)
                continue

            uname = name.upper()
            if uname == "BEGIN":
                self.handle_begin_component(vals)
            elif uname == "END":
                self.handle_end_component(vals)
            else:
                self.handle_property(uname, params, vals, line)

    @property
    def component(self) -> Component | None:
        return self._stack[-1] if self._stack else None

    def get_factory_for_property(self, name: str, params: Parameters) -> VPROPERTY:
        """Get the factory for a property."""
        return self._types_factory.for_property(name, params.value)

    def handle_property(
        self, name: str, params: Parameters, vals: str, line: Contentline
    ) -> None:
        """Handle a property line.

        We are adding properties to the current top of the stack

        Parameters:
            name: The name of the property, uppercased.
            params: The parameters of the property.
            vals: The value of the property.
            line: The original content line.
        """
        # Extract VALUE parameter if present
        if not self.component:
            # only accept X-COMMENT at the end of the .ics file
            # ignore these components in parsing
            if name == "X-COMMENT":
                return  # TODO: This was a break
            raise ValueError(f'Property "{name}" does not have a parent component.')
        # Determine TZID for datetime properties
        tzid = params.get("TZID") if params and name in self.datetime_names else None

        # Handle special cases for value list preparation
        if name == "CATEGORIES":
            if self.handle_categories(params, vals, line):
                return
            # Fallback to normal processing if we can't find colon
            vals_list = [vals]
        elif name == "FREEBUSY":
            # Handle FREEBUSY comma-separated values
            vals_list = vals.split(",")
        # Workaround broken ICS files with empty RDATE
        # (not EXDATE - let it parse and fail)
        elif name == "RDATE" and vals == "":
            vals_list = []
        else:
            vals_list = [vals]

        # Parse all properties eagerly
        for val in vals_list:
            self.parse_and_add_property(name, params, val, tzid, line)

    def parse_and_add_property(
        self,
        name: str,
        params: Parameters,
        val: str,
        tzid: str | None,
        line: Contentline,
    ):
        """Parse a property value and add it to the current component."""
        factory = self.get_factory_for_property(name, params)
        try:
            if tzid:
                parsed_val = factory.from_ical(val, tzid)
            else:
                parsed_val = factory.from_ical(val)
        except (ValueError, TypeError) as e:
            self.handle_property_parse_error(e, name, params, val, line)
        else:
            vals_inst = factory(parsed_val)
            vals_inst.params = params
            self.component.add(name, vals_inst, encode=False)

    def handle_property_parse_error(
        self,
        exception: Exception,
        name: str,
        params: Parameters,
        val: str,
        line: Contentline,
    ):
        """Handle the parse error for a property."""
        if not self.component.ignore_exceptions:
            raise exception
        # Error-tolerant mode: create vBroken
        factory = self.get_factory_for_property(name, params)
        expected_type = getattr(factory, "__name__", "unknown")
        broken_prop = vBroken.from_parse_error(
            raw_value=val,
            params=params,
            property_name=name,
            expected_type=expected_type,
            error=exception,
        )
        self.component.errors.append((name, str(exception)))
        self.component.add(name, broken_prop, encode=0)

    def handle_categories(
        self, params: Parameters, vals: str, line: Contentline
    ) -> bool:
        """Handle the special case of CATEGORIES property.

        Returns:
            True if handled, False if not.
        """
        # Special handling for CATEGORIES - need raw value
        # before unescaping to properly split on unescaped commas
        line_str = str(line)
        # Use rfind to get the last colon (value separator)
        # to handle parameters with colons like ALTREP="http://..."
        colon_idx = line_str.rfind(":")
        if colon_idx > 0:
            raw_value = line_str[colon_idx + 1 :]
            # Parse categories immediately (not lazily) for both
            # strict and tolerant components.
            # CATEGORIES needs special comma handling
            try:
                category_list = split_on_unescaped_comma(raw_value)
                factory = self.get_factory_for_property("CATEGORIES", params)
                vals_inst = factory(category_list)
                vals_inst.params = params
                self.component.add("CATEGORIES", vals_inst, encode=0)
            except ValueError as e:
                self.handle_property_parse_error(
                    e, "CATEGORIES", params, raw_value, line
                )
            return True
        return False
