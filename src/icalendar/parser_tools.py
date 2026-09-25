"""Tools for parsing."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.cal.component import Component
    from icalendar.prop import VPROPERTY

SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = "utf-8"
ICAL_TYPE = str | bytes


def from_unicode(value: ICAL_TYPE, encoding: str = "utf-8") -> bytes:
    """Converts a value to bytes, even if it is already bytes.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.

    Returns:
        The bytes representation of the value.
    """
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        try:
            return value.encode(encoding)
        except UnicodeEncodeError:
            return value.encode("utf-8", "replace")
    else:
        return value


def to_unicode(value: ICAL_TYPE, encoding: str = "utf-8-sig") -> str:
    """Converts a value to Unicode, even if it is already a Unicode string.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode("utf-8-sig", "replace")
    else:
        return value


def data_encode(
    data: ICAL_TYPE | dict | list, encoding: str = DEFAULT_ENCODING
) -> bytes | list[bytes] | dict:
    """Encode all datastructures to the given encoding.

    Currently Unicode strings, dicts, and lists are supported.

    Parameters:
        data: The datastructure to encode.
    """
    # https://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str
    if isinstance(data, str):
        return data.encode(encoding)
    if isinstance(data, dict):
        return dict(map(data_encode, iter(data.items())))
    if isinstance(data, (list, tuple)):
        return list(map(data_encode, data))
    return data


class XCalRegexMatcher:
    """Match a regex and provide some nice error message."""

    def __init__(self, regex: str | re.Pattern, expected_message: str, flags: int = 0):
        self._regex = (
            re.compile(f"^{regex}$", flags) if isinstance(regex, str) else regex
        )
        self._expected_message = expected_message

    def match(self, element: Element, parser: type[VPROPERTY | Component]) -> re.Match:
        """Return the match for the element.

        Parameters:
            element: The element to match the text from.

        Returns:
            The match if successful.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
        """
        from icalendar.error import XCalParsingError

        match = self._regex.match(element.text or "")
        if match is None:
            raise XCalParsingError.in_property_text(
                self._expected_message,
                element,
                parser,
            )
        return match

    def groups(self, element: Element, parser: type[VPROPERTY | Component]):
        """Return the match groups for the element.

        Parameters:
            element: The element to match the text from.

        Returns:
            The groups of the match if successful.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
        """
        return self.match(element, parser).groups()


__all__ = [
    "DEFAULT_ENCODING",
    "ICAL_TYPE",
    "SEQUENCE_TYPES",
    "XCalRegexMatcher",
    "data_encode",
    "from_unicode",
    "to_unicode",
]
