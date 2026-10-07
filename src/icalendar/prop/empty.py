"""This is an value type for an empty icalendar property.

The calendar is invalid.
This eases round trip and corrections.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from icalendar.error import InvalidCalendar
from icalendar.parser.xcal.wrapper import from_xcal_wrapper

from .unknown import vUnknown

if TYPE_CHECKING:
    from icalendar.compatibility import Self
    from icalendar.parser.parameter import Parameters
    from icalendar.parser.xcal.base import XCalParser


class vEmtpy(vUnknown):
    """An empty icalendar property."""

    def __new__(
        cls,
        /,
        params: dict[str, Any] | None = None,
    ) -> Self:
        return super().__new__(cls, "", params=params)

    @property
    def ical_value(self) -> str:
        """This property is empty and has no value.

        Raises:
            InvalidCalendar: Always.
        """
        raise InvalidCalendar("No property value given.")

    @classmethod
    @from_xcal_wrapper
    def from_xcal(cls, parser: XCalParser, params: Parameters) -> Self:  # noqa: ARG003
        """Parse xCal from :rfc:`6321`.

        This does not parse any tag but instead assumes that there is no tag.

        Parameters:
            parser: The parser to use.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        params.value = cls.default_value  # UNKNOWN is never the default type
        return cls(params=params)


__all__ = ["vEmtpy"]
