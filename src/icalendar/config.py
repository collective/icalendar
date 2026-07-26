"""Runtime configuration for icalendar."""

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
