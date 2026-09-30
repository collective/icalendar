"""Convenience methods for parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar
from xml.etree.ElementTree import Element

from icalendar.parser.xcal.adapter import ElementAdapter

if TYPE_CHECKING:
    from collections.abc import Callable

    from icalendar.parser.parameter import Parameters
    from icalendar.parser.xcal.base import XCalParser

VProp = TypeVar("VProp")

# Trying to solve typing issues: https://stackoverflow.com/q/80005905/1320237


def from_xcal_wrapper(
    func: Callable[[type[VProp], XCalParser, Parameters], VProp],
) -> Callable[[type[VProp], XCalParser | ElementAdapter | Element], VProp]:
    """Wrap a property's from_xcal() with convenience functions.

    Use it below ``@classmethod`` so that type checkers and linters see
    a class method.
    """

    def wrapper(cls: type[VProp], xml: XCalParser | ElementAdapter | Element) -> VProp:
        if isinstance(xml, (Element, ElementAdapter)):
            from icalendar.parser.xcal.property import XCalPropertyParser

            xml = XCalPropertyParser(xml)
        parameters = xml.parse_parameters()
        return func(cls, xml, parameters)

    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__doc__ = func.__doc__

    return wrapper


__all__ = [
    "from_xcal_wrapper",
]
