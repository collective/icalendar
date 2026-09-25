"""Convenience methods for parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar
from xml.etree.ElementTree import Element

from icalendar.parser.xcal.property import XCalPropertyParser

if TYPE_CHECKING:
    from collections.abc import Callable

    from icalendar.parser.parameter import Parameters
    from icalendar.parser.xcal.value import VPropParser

VProp = TypeVar("VProp")


def from_xcal_wrapper(
    func: Callable[[type[VProp], VPropParser, Parameters], VProp],
) -> Callable[[type[VProp], VPropParser | Element], VProp]:
    """Wrap a property's from_xcal() with convenience functions."""

    @classmethod
    def wrapper(cls: type[VProp], xml: VPropParser | Element) -> VProp:
        if isinstance(xml, Element):
            xml = XCalPropertyParser(xml)
        parameters = xml.parse_parameters()
        return func(cls, xml, parameters)

    return wrapper


__all__ = [
    "from_xcal_wrapper",
]
