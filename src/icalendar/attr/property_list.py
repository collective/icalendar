"""A list-like view for RFC 5545 component property values."""

from __future__ import annotations

import contextlib
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

    from icalendar.cal.component import Component


class PropertyListView(MutableSequence):
    """A list-like view of an RFC 5545 property within a component.

    This view synchronizes modifications (such as append, extend, insert,
    clear, and delete) with the underlying component dictionary.
    """

    __hash__ = None

    def __init__(self, component: Component, name: str) -> None:
        """Initialize the property list view for a given component and property name."""
        self._component = component
        self._name = name

    @contextlib.contextmanager
    def _values(self) -> Iterator[list[Any]]:
        """Synchronize the value list with the component."""
        raw = self._component.get(self._name, [])
        values = [raw] if not isinstance(raw, list) else list(raw)
        try:
            yield values
        finally:
            if not values:
                self._component.pop(self._name, None)
            else:
                self._component[self._name] = values

    def __getitem__(self, index: Any) -> Any:
        """Get an item or slice from the property list."""
        with self._values() as values:
            return values[index]

    def __setitem__(self, index: Any, value: Any) -> None:
        """Set an item or slice in the property list."""
        with self._values() as values:
            values[index] = value

    def __delitem__(self, index: Any) -> None:
        """Delete an item or slice from the property list."""
        with self._values() as values:
            del values[index]

    def __len__(self) -> int:
        """Return the number of items in the property list."""
        raw = self._component.get(self._name, [])
        if not raw:
            return 0
        if not isinstance(raw, list):
            return 1
        return len(raw)

    def insert(self, index: int, value: Any) -> None:
        """Insert an item into the property list at a given index."""
        with self._values() as values:
            values.insert(index, value)

    def __eq__(self, other: object) -> bool:
        """Check equality against another sequence."""
        if isinstance(other, PropertyListView):
            return list(self) == list(other)
        if hasattr(other, "__iter__"):
            return list(self) == list(other)
        return False

    def __repr__(self) -> str:
        """Return the string representation of the property list view."""
        return f"PropertyListView({list(self)!r})"


__all__ = ["PropertyListView"]
