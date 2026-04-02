from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, TypeVar

from icalendar.parser_tools import to_unicode

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

KT = TypeVar("KT")
VT = TypeVar("VT")


def canonsort_keys(
    keys: Iterable[KT], canonical_order: Iterable[KT] | None = None
) -> list[KT]:
    """Sort leading keys according to a canonical order.

    Keys specified in ``canonical_order`` appear first in that order.
    Remaining keys appear alphabetically at the end.

    Parameters:
        keys: The keys to sort.
        canonical_order: The preferred order for leading keys.
            Keys not in this sequence are sorted alphabetically after
            the canonical ones. If ``None``, all keys are sorted
            alphabetically.

    Returns:
        A new list of keys sorted by canonical order first, then alphabetically.

    Example:
        .. code-block:: pycon

            >>> from icalendar.caselessdict import canonsort_keys
            >>> canonsort_keys(["C", "A", "B"], ["B", "C"])
            ['B', 'C', 'A']
    """
    canonical_map = {k: i for i, k in enumerate(canonical_order or [])}
    head = [k for k in keys if k in canonical_map]
    tail = [k for k in keys if k not in canonical_map]
    return sorted(head, key=lambda k: canonical_map[k]) + sorted(tail)


def canonsort_items(
    dict1: Mapping[KT, VT], canonical_order: Iterable[KT] | None = None
) -> list[tuple[KT, VT]]:
    """Sort items from a mapping according to a canonical key order.

    Returns ``(key, value)`` pairs sorted using :func:`canonsort_keys`.

    Parameters:
        dict1: The mapping whose items to sort.
        canonical_order: The preferred order for leading keys.
            If ``None``, all keys are sorted alphabetically.

    Returns:
        A list of ``(key, value)`` tuples sorted by canonical order.

    Example:
        .. code-block:: pycon

            >>> from icalendar.caselessdict import canonsort_items
            >>> canonsort_items({"C": 3, "A": 1, "B": 2}, ["B", "C"])
            [('B', 2), ('C', 3), ('A', 1)]
    """
    return [(k, dict1[k]) for k in canonsort_keys(dict1.keys(), canonical_order)]


class CaselessDict(OrderedDict):
    """A case-insensitive dictionary that uses strings as keys.

    All keys are stored in uppercase internally, but values retain
    their original case. Keys can be provided as ``str`` or ``bytes``;
    they are converted to Unicode via :func:`~icalendar.parser_tools.to_unicode`
    and then uppercased before storage.

    Example:
        .. code-block:: pycon

            >>> from icalendar.caselessdict import CaselessDict
            >>> d = CaselessDict(summary="Meeting")
            >>> d["SUMMARY"]
            'Meeting'
            >>> "summary" in d
            True
    """

   """

def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a new ``CaselessDict`` and normalize existing keys to uppercase.

        Parameters:
            *args: Positional arguments passed to :class:`~collections.OrderedDict`.
            **kwargs: Keyword arguments passed to :class:`~collections.OrderedDict`.


        Example:
            .. code-block:: pycon

                >>> from icalendar.caselessdict import CaselessDict
                >>> d = CaselessDict(summary="Meeting")
                >>> d["SUMMARY"]
                'Meeting'
                >>> "summary" in d
                True
        """
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            key_upper = to_unicode(key).upper()
            if key != key_upper:
                super().__delitem__(key)
                self[key_upper] = value

    __hash__ = None

    def __getitem__(self, key: Any) -> Any:
        """Return the value for ``key``, case-insensitively.

        Parameters:
            key: The key to look up, case-insensitively.

        Returns:
            The value associated with the uppercased key.

        Raises:
            KeyError: If the key is not found.
        """
        key = to_unicode(key)
        return super().__getitem__(key.upper())

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set a value, storing the key in uppercase.

        Parameters:
            key: The key to set (case-insensitive).
            value: The value to associate with the key.
        """
        key = to_unicode(key)
        super().__setitem__(key.upper(), value)

    def __delitem__(self, key: Any) -> None:
        """Delete a key-value tuple by its case-insensitive key.

        Parameters:
            key: The key to delete, case-insensitively.

        Raises:
            KeyError: If the key is not found.
        """
        key = to_unicode(key)
        super().__delitem__(key.upper())

    def __contains__(self, key: Any) -> bool:
        """Check whether a key exists, case-insensitively.

        Parameters:
            key: The key to check case-insensitively.

        Returns:
            ``True`` if the uppercased key exists, ``False`` otherwise.
        """
        key = to_unicode(key)
        return super().__contains__(key.upper())

    def get(self, key: Any, default: Any = None) -> Any:
        """Return the value for ``key`` if present, otherwise ``default``.

        Parameters:
            key: The key to look up, case-insensitively.
            default: The value to return if the key is not found.

        Returns:
            The value for the key, or ``default``.
        """
        key = to_unicode(key)
        return super().get(key.upper(), default)

    def setdefault(self, key: Any, value: Any = None) -> Any:
        """Return the value for ``key``, setting it to ``value`` if not present.

        Parameters:
            key: The key to look up or create, case-insensitively.
            value: The default value to set if the key does not exist.

        Returns:
            The existing or newly set value.
        """
        key = to_unicode(key)
        return super().setdefault(key.upper(), value)

    def pop(self, key: Any, default: Any = None) -> Any:
        """Remove and return the value for ``key``, or ``default`` if not found.

        Parameters:
            key: The key to remove, case-insensitively.
            default: The value to return if the key is not found.

        Returns:
            The removed value, or ``default``.
        """
        key = to_unicode(key)
        return super().pop(key.upper(), default)

    def popitem(self) -> tuple[Any, Any]:
        """Remove and return the last inserted ``(key, value)`` pair.

        Returns:
            A ``(key, value)`` tuple.

        Raises:
            KeyError: If the dictionary is empty.
        """
        return super().popitem()

    def has_key(self, key: Any) -> bool:
        """Check whether a key exists, case-insensitively.

        This is a legacy method; prefer using ``key in dict`` instead.

        Parameters:
            key: The key to check case-insensitively.

        Returns:
            ``True`` if the uppercased key exists, ``False`` otherwise.
        """
        key = to_unicode(key)
        return super().__contains__(key.upper())

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update the dictionary with key-value pairs, normalizing keys to uppercase.

        Multiple keys that differ only in case will overwrite each other;
        only the last value is retained.

        Parameters:
            *args: Mappings or iterables of ``(key, value)`` pairs.
            **kwargs: Additional key-value pairs.
        """
        # Multiple keys where key1.upper() == key2.upper() will be lost.
        mappings = list(args) + [kwargs]
        for mapping in mappings:
            if hasattr(mapping, "items"):
                mapping = iter(mapping.items())  # noqa: PLW2901
            for key, value in mapping:
                self[key] = value

    def copy(self) -> Self:
        """Return a shallow copy of the dictionary.

        Returns:
            A new instance of the same type with the same contents.
        """
        return type(self)(super().copy())

    def __repr__(self) -> str:
        """Return a string representation of the dictionary.

        Returns:
            A string in the form ``CaselessDict({...})``.
        """
        return f"{type(self).__name__}({dict(self)})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another dictionary.

        Two ``CaselessDict`` instances are equal if they contain the same
        key-value pairs (after uppercasing keys). Comparison with a regular
        ``dict`` also works.

        Parameters:
            other: The object to compare.

        Returns:
            ``True`` if equal, ``NotImplemented`` if ``other`` is not a ``dict``.
        """
        if not isinstance(other, dict):
            return NotImplemented
        return self is other or dict(self.items()) == dict(other.items())

    def __ne__(self, other: object) -> bool:
        """Check inequality with another dictionary.

        Parameters:
            other: The object to compare.

        Returns:
            ``True`` if not equal.
        """
        return not self == other

    # A list of keys that must appear first in sorted_keys and sorted_items;
    # must be uppercase.
    canonical_order = None

    def sorted_keys(self) -> list[str]:
        """Sort keys according to the canonical order for this class.

        Keys listed in :attr:`canonical_order` appear first in that order.
        Remaining keys appear alphabetically at the end.

        Returns:
            A sorted list of keys.
        """
        return canonsort_keys(self.keys(), self.canonical_order)

    def sorted_items(self) -> list[tuple[Any, Any]]:
        """Sort items according to the canonical order for this class.

        Items whose keys are listed in :attr:`canonical_order` appear first
        in that order. Remaining items appear alphabetically by key.

        Returns:
            A sorted list of ``(key, value)`` tuples.
        """
        return canonsort_items(self, self.canonical_order)


__all__ = ["CaselessDict", "canonsort_items", "canonsort_keys"]
