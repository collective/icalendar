from __future__ import annotations

import re
from typing import TYPE_CHECKING

from icalendar.error import XCalParsingError

if TYPE_CHECKING:
    from icalendar.parser.xcal.adapter import ElementAdapter


class XCalRegexMatcher:
    """Match a regex and provide some nice error message."""

    def __init__(self, regex: str | re.Pattern, expected_message: str, flags: int = 0):
        self._regex = (
            re.compile(f"^{regex}$", flags) if isinstance(regex, str) else regex
        )
        self._expected_message = expected_message

    def match(self, element: ElementAdapter) -> re.Match:
        """Return the match for the element.

        Parameters:
            element: The element to match the text from.

        Returns:
            The match if successful.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
        """

        match = self._regex.match(element.get_xsd_string())
        if match is None:
            raise XCalParsingError(
                self._expected_message,
                element.get_xsd_string(),
                element,
            )
        return match

    def groups(self, element: ElementAdapter):
        """Return the match groups for the element.

        Parameters:
            element: The element to match the text from.

        Returns:
            The groups of the match if successful.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
        """
        return self.match(element).groups()


__all__ = ["XCalRegexMatcher"]
