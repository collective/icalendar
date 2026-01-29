from __future__ import annotations

from icalendar.parser_tools import to_unicode

from collections import OrderedDict

from typing import Any, Optional, Iterable, Mapping, TypeVar

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

KT = TypeVar("KT")
VT = TypeVar("VT")

def canonsort_keys(keys: Iterable[KT], canonical_order: Optional[Iterable[KT]] = None) -> list[KT]:
    """Sort keys according to a canonical order with remaining keys alphabetically at the end.

    Keys specified in canonical_order appear first in the order they are defined,
    followed by any remaining keys sorted alphabetically.

    Args:
        keys: An iterable of keys to be sorted.
        canonical_order: An optional iterable defining the preferred order for leading keys.
            Keys not in this iterable will appear alphabetically at the end.

    Returns:
        A list of keys sorted according to the canonical order, with unspecified
        keys appearing alphabetically at the end.

    Examples:
        >>> canonsort_keys(['b', 'a', 'c'], ['c', 'a'])
        ['c', 'a', 'b']
        >>> canonsort_keys(['x', 'y', 'z'])
        ['x', 'y', 'z']
    """
    canonical_map = {k: i for i, k in enumerate(canonical_order or [])}
    head = [k for k in keys if k in canonical_map]
    tail = [k for k in keys if k not in canonical_map]
    return sorted(head, key=lambda k: canonical_map[k]) + sorted(tail)


def canonsort_items(dict1: Mapping[KT, VT], canonical_order: Optional[Iterable[KT]] = None) -> list[tuple[KT, VT]]:
    """Return a list of key-value pairs from a dictionary, sorted by canonical order.

    This function extracts items from the given dictionary and returns them as a list
    of tuples, sorted according to the specified canonical order.

    Args:
        dict1: The dictionary whose items are to be sorted.
        canonical_order: An optional iterable defining the preferred order for keys.
            Keys not in this iterable will appear alphabetically at the end.

    Returns:
        A list of (key, value) tuples sorted according to the canonical order.

    Examples:
        >>> canonsort_items({'b': 2, 'a': 1, 'c': 3}, ['c', 'a'])
        [('c', 3), ('a', 1), ('b', 2)]
    """
    return [(k, dict1[k]) for k in canonsort_keys(dict1.keys(), canonical_order)]


class CaselessDict(OrderedDict):
    """A dictionary that isn't case sensitive, and only uses strings as keys.

    Values retain their case. All keys are converted to uppercase internally,
    but lookups are case-insensitive.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the CaselessDict and convert all keys to uppercase.

        Args:
            *args: Positional arguments passed to OrderedDict.
            **kwargs: Keyword arguments passed to OrderedDict.
        """
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            key_upper = to_unicode(key).upper()
            if key != key_upper:
                super().__delitem__(key)
                self[key_upper] = value

    def __getitem__(self, key: Any) -> Any:
        key = to_unicode(key)
        return super().__getitem__(key.upper())

    def __setitem__(self, key: Any, value: Any) -> None:
        key = to_unicode(key)
        super().__setitem__(key.upper(), value)

    def __delitem__(self, key: Any) -> None:
        key = to_unicode(key)
        super().__delitem__(key.upper())

    def __contains__(self, key: Any) -> bool:
        key = to_unicode(key)
        return super().__contains__(key.upper())

    def get(self, key: Any, default: Any = None) -> Any:
        key = to_unicode(key)
        return super().get(key.upper(), default)

    def setdefault(self, key: Any, value: Any = None) -> Any:
        key = to_unicode(key)
        return super().setdefault(key.upper(), value)

    def pop(self, key: Any, default: Any = None) -> Any:
        key = to_unicode(key)
        return super().pop(key.upper(), default)

    def popitem(self) -> tuple[Any, Any]:
        return super().popitem()

    def has_key(self, key: Any) -> bool:
        key = to_unicode(key)
        return super().__contains__(key.upper())

    def update(self, *args: Any, **kwargs: Any) -> None:
        # Multiple keys where key1.upper() == key2.upper() will be lost.
        mappings = list(args) + [kwargs]
        for mapping in mappings:
            if hasattr(mapping, "items"):
                mapping = iter(mapping.items())
            for key, value in mapping:
                self[key] = value

    def copy(self) -> Self:
        return type(self)(super().copy())

    def __repr__(self) -> str:
        return f"{type(self).__name__}({dict(self)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, dict):
            return NotImplemented
        return self is other or dict(self.items()) == dict(other.items())

    def __ne__(self, other: object) -> bool:
        return not self == other

    # A list of keys that must appear first in sorted_keys and sorted_items;
    # must be uppercase.
    canonical_order = None

    def sorted_keys(self) -> list[str]:
        """Return keys sorted according to the canonical order for this class.

        Keys specified in the class's canonical_order attribute appear first,
        followed by remaining keys in alphabetical order.

        Returns:
            A list of keys sorted by canonical order, with unspecified keys
            appearing alphabetically at the end.
        """
        return canonsort_keys(self.keys(), self.canonical_order)

    def sorted_items(self) -> list[tuple[Any, Any]]:
        """Return items sorted according to the canonical order for this class.

        Items are sorted by their keys according to the class's canonical_order
        attribute, with unspecified keys appearing alphabetically at the end.

        Returns:
            A list of (key, value) tuples sorted by canonical order.
        """
        return canonsort_items(self, self.canonical_order)


__all__ = ["canonsort_keys", "canonsort_items", "CaselessDict"]
