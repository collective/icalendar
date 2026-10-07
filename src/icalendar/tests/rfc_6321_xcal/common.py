"""Common xCal test functionality."""

from __future__ import annotations

from typing import Protocol
from xml.etree.ElementTree import Element, tostring


class HasToXcal(Protocol):
    def to_xcal(self, element: Element) -> None: ...


def to_xcal(value: HasToXcal, wrap=False) -> Element:
    """Return the xCal of a component.

    Parameters:
        value: The value to serialize
        wrap: Wrap the value in an element

    Returns:
        The serialized Element or a wrapper when the value created several elements.
    """
    e = Element("TEST")
    value.to_xcal(e)
    assert wrap or len(e) != 0, (
        f"{value.__class__.__name__} did not generate xCal content."
    )
    if len(e) == 1 and not wrap:
        e = e[0]  # for components
    print(tostring(e, method="xml").decode())
    return e


XML_WHITESPACE = "\x09\x0a\x0d\x20"
"""Whitespace is treated differently in XML than in iCalendar.

See:
- Definition: https://www.w3.org/TR/xmlschema-1/#d0e1654
- Credit: https://stackoverflow.com/a/666338
- "White Space: collapse": https://datypic.com/sc/xsd/t-xsd_float.html

"""


def list2xml(spec: list[str | list]) -> Element[str]:
    """Generate and xml tree from a specification.

    Args:
        spec: A spec.
    """
    if not isinstance(spec, list):
        raise TypeError("spec must be a list.")
    if not spec:
        raise ValueError("spec must not be empty.")
    if not isinstance(spec[0], str):
        raise TypeError("spec[0] must be a string.")
    e = Element(spec[0].lower())
    if len(spec) == 1:
        return e
    index = 1
    if isinstance(spec[1], str):
        e.text = spec[1]
        index = 2
    for child in spec[index:]:
        e.append(list2xml(child))  # pyright: ignore[reportArgumentType]
    return e


def xml2list(element: Element[str]) -> list[str | list]:
    """Return the reverse of :func:`list2xml`."""
    children = [xml2list(child) for child in element]
    if not children:
        return [element.tag, str(element.text or "")]
    return [element.tag] + children


def to_xcal_list(value: HasToXcal, wrap: bool = True) -> list[str | list]:
    """combile to_xcal and xml2list."""
    return xml2list(to_xcal(value, wrap=wrap))


INVALID_DATES = [
    "0000-01-01",
    # "9999-01-12",  # valid
    "2026-00-01",
    "2025-13-01",
    "2025-01-32",
    "2025-02-30",
    "2025-02-00",
]
"""Dates out of range.

See https://www.rfc-editor.org/info/rfc5545/#section-3.3.4
"""


INVALID_TIMES = [
    "24:00:00",
    "00:60:00",
    "00:00:61",
]
"""Invalid strings for times.

time-hour    = 2DIGIT        ;00-23
time-minute  = 2DIGIT        ;00-59
time-second  = 2DIGIT        ;00-60
"""
