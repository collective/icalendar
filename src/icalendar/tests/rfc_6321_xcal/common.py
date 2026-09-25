"""Common xCal test functionality."""

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


def generate_xml_tree(spec: list[str | list]) -> Element:
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
        e.append(generate_xml_tree(child))  # pyright: ignore[reportArgumentType]
    return e
