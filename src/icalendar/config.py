"""Runtime configuration for icalendar."""

MAX_ALARM_REPEAT: int = 10_000
"""Cap on additional triggers expanded from a ``VALARM`` ``REPEAT`` property.

:rfc:`5545` Section 3.8.6.2 defines ``REPEAT`` as a non-negative integer with no upper
bound, so a crafted value can exhaust memory or CPU. Set to ``-1`` to disable the cap
(only safe for fully trusted input).
"""


def _clamp_repeat(n: int) -> int:
    """Return *n* clamped to ``[0, MAX_ALARM_REPEAT]``.

    Negative values are treated as 0. When :data:`MAX_ALARM_REPEAT` is ``-1``
    the value is returned unchanged after clamping negatives to 0.
    """
    if n < 0:
        return 0
    if MAX_ALARM_REPEAT == -1:
        return n
    return min(n, MAX_ALARM_REPEAT)
