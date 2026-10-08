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


class vEmpty(vUnknown):
    """This represents an invalid, empty property that is still there.

    This is used when  a property element is present but carries no typed value,
    only parameters.
    Storing this placeholder keeps the parameters from being
    silently dropped when parsing,
    while :attr:`ical_value` raises so the
    broken state is visible.

    Properties containing :class:`vEmpty` are invalid.
    However, they will be serialized correctly, repairing the calendar.

    Examples:

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> cal = Calendar.from_xcal(
            ... b'''
            ... <icalendar>
            ...   <vcalendar>
            ...     <properties>
            ...       <version>
            ...         <parameters>
            ...           <x-param><text>x-content</text></x-param>
            ...         </parameters>
            ...         <!-- missing a value here -->
            ...       </version>
            ...     </properties>
            ...   </vcalendar>
            ... </icalendar>
            ... '''
            ... )[0]
            >>> cal["VERSION"]
            vEmpty()
            >>> cal["VERSION"].params["x-param"]
            'x-content'
    """

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

    def __repr__(self) -> str:
        """The text representation."""
        return f"{self.__class__.__name__}()"


__all__ = ["vEmpty"]
