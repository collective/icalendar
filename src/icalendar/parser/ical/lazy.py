"""Special parsing for calendar components."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from icalendar.parser.content_line import Contentline

from .component import ComponentIcalParser

if TYPE_CHECKING:
    from icalendar.cal.component import Component


class LazyCalendarIcalParser(ComponentIcalParser):
    """A parser for calendar components.

    Instead of parsing the components, LazyComponents are created.
    Parsing can happen on demand.

    We assume that a calendar grows over time and that the subcomponents
    of the calendar become more in number.
    This optimization allows us to parse big calendar files without consuming
    more memory than necessary and reducing the initial time it takes to access
    meta data.
    """

    parse_instantly: ClassVar[tuple[str, ...]] = ("VCALENDAR",)
    """Parse these components instantly, instead of lazily.

    All other components are parsed lazily.
    """

    def handle_begin_component(self, vals):
        """Begin a new component.

        This could well be the first component.
        """
        c_name = vals.upper()
        if c_name in self.parse_instantly or not self.component:
            # these components are parsed instantly
            super().handle_begin_component(vals)
        else:
            self.handle_lazy_begin_component(c_name)

    def handle_lazy_begin_component(self, component_name: str) -> None:
        """Begin a new component, but do not parse it yet.

        Parameters:
            component_name:
                The upper case name of the component, for example, ``"VEVENT"``.
        """
        content_lines = [Contentline(f"BEGIN:{component_name}")]
        for line in self._content_lines_iterator:
            content_lines.append(line)
            if (
                line[:4].upper() == "END:"
                and line[4:].strip().upper() == component_name
            ):
                break
        assert self.component is not None
        self.component.add_component(
            LazySubcomponent(
                component_name,
                self.get_subcomponent_parser(content_lines),
            )
        )

    def get_subcomponent_parser(
        self, content_lines: list[Contentline]
    ) -> ComponentIcalParser:
        """Get the parser for a subcomponent.

        Parameters:
            content_lines: The content lines of the subcomponent.
        """
        return ComponentIcalParser(
            content_lines, self._component_factory, self._types_factory
        )

    def prepare_components(self):
        """Prepare the lazily parsed components."""


class LazySubcomponent:
    """A subcomponent that is evaluated lazily.

    This class holds the raw data of the subcomponent ready for parsing.
    """

    def __init__(self, name: str, parser: ComponentIcalParser):
        """Initialize the lazy subcomponent with the raw data."""
        self._name = name
        self._parser = parser
        self._component: Component | None = None

    @property
    def name(self) -> str:
        """The name of the subcomponent.

        This is upper case, as per RFC 5545.
        """
        return self._name

    def is_parsed(self) -> bool:
        """Return whether the subcomponent is already parsed."""
        return self._component is not None

    def parse(self) -> Component:
        """Parse the raw data and return the component."""
        if self._component is None:
            components = self._parser.parse()
            if len(components) != 1:
                raise ValueError(
                    f"Expected exactly one component in the subcomponent, "
                    f"but got {len(components)}."
                )
            self._component = components[0]
            self._parser = None  # free memory
        return self._component

    def is_lazy(self) -> bool:
        """You need to call :meth:`parse` to get the fully parsed component."""
        return True


__all__ = ["LazyCalendarIcalParser", "LazySubcomponent"]
