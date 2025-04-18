"""Attributes of Components and properties."""
from __future__ import annotations

from typing import Optional


def multi_language_text_property(main_prop:str, compatibility_prop:str, doc:str) -> property:
    """This creates a text property.

    This property can be defined several times with different LANGAUGE parameters.

    Args:

        main_prop: The property to set and get, e.g. NAME
        compatibility_prop: An old property used before, e.g. X-WR-CALNAME
        doc: The documentation string
    """
    def fget(self) -> Optional[str]:
        """Get the property"""
        result = self.get(main_prop, self.get(compatibility_prop))
        if isinstance(result, list):
            for item in result:
                if "LANGUAGE" not in item.params:
                    return item
        return result

    def fset(self, value:str):
        """Set the property."""
        fdel(self)
        self.add(main_prop, value)

    def fdel(self):
        """Delete the property."""
        self.pop(main_prop, None)
        self.pop(compatibility_prop, None)

    return property(fget, fset, fdel, doc)


__all__ = ["multi_language_text_property"]
