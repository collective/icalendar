from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from icalendar.parser.parameter import Parameters
    from icalendar.parser.xcal.adapter import ElementAdapter


class VPropParser(Protocol):
    """This the interface that the value types in icalendar.prop use.

    Classes that implement this:

    * :class:`~icalendar.parser.ical.parameters.XCalParameterParser`
    """

    def parse_parameters(self) -> Parameters: ...

    def parse_tag(self, tag: str) -> ElementAdapter: ...
