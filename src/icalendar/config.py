"""Runtime configuration for icalendar."""

MAX_ALARM_REPEAT: int = 10_000
"""Cap on additional triggers expanded from a ``VALARM`` ``REPEAT`` property.

:rfc:`5545#section-3.8.6.2` defines ``REPEAT`` as an ``INTEGER`` (:rfc:`5545#section-3.3.8`),
which is bounded between -2147483648 and 2147483647. Even within that range, a value
near the maximum can exhaust memory or CPU. Set to ``-1`` to disable the cap,
which should be done only for fully trusted input.
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
