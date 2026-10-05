"""Runtime configuration for icalendar."""

from xml.etree.ElementTree import Element, ElementTree, parse

MAX_ALARM_REPEAT: int = 10_000
"""Cap on additional triggers expanded from a ``VALARM`` ``REPEAT`` property.

:rfc:`5545#section-3.8.6.2` defines ``REPEAT`` as an ``INTEGER`` data type, which is
defined in :rfc:`5545#section-3.3.8` as an integer between -2147483648 and 2147483647.
A value for ``REPEAT`` that is greater than approximately ``10_000`` can exhaust memory
or CPU. The default value of ``10_000`` is a practical setting, but may be adjusted to
specific use cases. Set to ``-1`` to disable the cap, which should be done only for
fully trusted input.

.. versionadded:: 7.2.1
"""


def _clamp_repeat(n: int) -> int:
    """Return *n* clamped to ``[0, MAX_ALARM_REPEAT]``.

    Negative values are treated as 0. When :data:`MAX_ALARM_REPEAT` is ``-1``
    the value is returned unchanged after clamping negatives to 0.
    """
    if n < 0:
        return 0
    if MAX_ALARM_REPEAT < 0:
        return n
    return min(n, MAX_ALARM_REPEAT)


def parse_xml(source) -> ElementTree[Element[str]]:
    """Parse xml from source.

    This wraps :func:`xml.etree.ElementTree.parse`.
    It makes the XML parser configurable.

    If you would like to use another XML parser,
    you can replace this function.

    .. seealso::

        :ref:`safe-xml-parsing`

    Parameters:
        source: A file-like object to with a ``read`` method.

    Returns:
        The parsed XML tree.

    Raises:
        TypeError: If the wrong type is passed to ``source``.

    """
    if not hasattr(source, "read"):
        raise TypeError("Expected source.read() method.")
    # S314 Using `xml` to parse untrusted data is known to be vulnerable to XML attacks
    return parse(source)  # noqa: S314


__all__ = [
    "MAX_ALARM_REPEAT",
    "parse_xml",
]
