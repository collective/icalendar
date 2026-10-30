"""A list-like view for :rfc:`5545#section-3.8` component property values."""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator, MutableSequence, Sequence
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from icalendar.prop import vText

if TYPE_CHECKING:
    from icalendar.cal.component import Component

ValueT = TypeVar("ValueT")
ArgT = TypeVar("ArgT")


class PropertyListView(MutableSequence[ValueT], Generic[ValueT, ArgT]):
    """A list-like view of an :rfc:`5545#section-3.8` property within a component.

    This view synchronizes modifications, such as ``append``, ``extend``, ``insert``,
    ``clear``, and ``delete``, with the underlying component dictionary.
    """

    __hash__ = None

    def __init__(
        self,
        component: Component,
        name: str,
        converter: Callable[[ArgT], ValueT] | dict[type, type] | None = None,
    ) -> None:
        """Initialize the property list view for a given component and property name.

        Parameters:
            component: The component to view.
            name: The name of the property to view.
            converter: An optional conversion function or mapping from types to
                conversion classes used when inserting or modifying values.
        """
        self._component = component
        self._name = name
        self._converter = converter

    @classmethod
    def for_text(
        cls, component: Component, name: str
    ) -> PropertyListView[vText, str | vText]:
        """Create a PropertyListView for text properties converting strings to vText."""
        return cls(
            component,
            name,
            converter=lambda v: v if isinstance(v, vText) else vText(v),
        )

    def _convert(self, value: Any) -> Any:
        """Convert a value using the configured converter if present."""
        if self._converter is None:
            return value
        if isinstance(self._converter, dict):
            target_cls = self._converter.get(type(value))
            if target_cls is not None:
                return target_cls(value)
            return value
        if callable(self._converter):
            return self._converter(value)
        return value

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
            if isinstance(index, slice):
                values[index] = [self._convert(v) for v in value]
            else:
                values[index] = self._convert(value)

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
        """Insert an item into the property list at a given index.

        Parameters:
            index: The position at which to insert the item into the property list.
            value: The value to insert in the property list at the given index.
        """
        converted = self._convert(value)
        with self._values() as values:
            values.insert(index, converted)

    def clear(self) -> None:
        """Remove all values and the property from the component."""
        self._component.pop(self._name, None)

    def replace_with(self, values: Any) -> None:
        """Replace all values in the property with ``values``.

        The values are added with
        :meth:`Component.add <icalendar.cal.component.Component.add>`,
        so they are converted to the correct types.

        Parameters:
            values: The values to replace in the property list.
                ``None`` removes all values from the property,
                whereas a single string value or any sequence type
                replaces all values in the property and is stored as a list.
        """
        if values is None:
            new_values = []
        elif isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            # copy first: ``values`` could be this view or a view of this property
            new_values = list(values)
        else:
            new_values = [values]
        self.clear()
        for value in new_values:
            self._component.add(self._name, value)

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

    def __add__(self, other: Any) -> list[Any]:
        """Concatenate this list with a sequence and return a new list."""
        if isinstance(other, Sequence) and not isinstance(other, (str, bytes)):
            return list(self) + list(other)
        return NotImplemented

    def __radd__(self, other: Any) -> list[Any]:
        """Concatenate a sequence with this list and return a new list."""
        if isinstance(other, Sequence) and not isinstance(other, (str, bytes)):
            return list(other) + list(self)
        return NotImplemented

    def __mul__(self, n: int) -> list[Any]:
        """Multiply the property list by an integer to return a new repeated list."""
        if isinstance(n, int):
            return list(self) * n
        return NotImplemented

    def __rmul__(self, n: int) -> list[Any]:
        """Multiply the property list by an integer to return a new repeated list."""
        if isinstance(n, int):
            return list(self) * n
        return NotImplemented

    def copy(self) -> list[Any]:
        """Return a shallow copy of the property list as a regular list."""
        return list(self)


__all__ = ["PropertyListView"]
