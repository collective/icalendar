"""Regression test for repr() RecursionError on deeply-nested calendars.

See https://github.com/collective/icalendar/issues/1370.

A crafted ``.ics`` payload of only ~13 KB nesting ``BEGIN:VEVENT``
many levels deep used to make ``repr()`` / ``str()`` / ``f"{cal}"``
raise an uncaught ``RecursionError`` at default recursion limit (1000).

The parser itself is iterative and accepts the input fine; only the
``Component.__repr__`` traversal was recursive. This test exercises both
moderate (default-recursion-limit-breaking) and pathological depths.
"""

import pytest

from icalendar import Calendar


def _make_nested_calendar(depth: int) -> str:
    """Return an .ics payload with ``depth`` levels of nested VEVENT."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//test//test//EN"]
    lines += ["BEGIN:VEVENT"] * depth
    lines += ["UID:nested@example.com", "DTSTAMP:20260101T000000Z"]
    lines += ["END:VEVENT"] * depth
    lines += ["END:VCALENDAR"]
    return "\r\n".join(lines) + "\r\n"


@pytest.mark.parametrize("depth", [10, 100, 500, 1000])
def test_repr_does_not_raise_recursion_error(depth):
    """``repr()`` must not raise ``RecursionError`` regardless of depth."""
    ics = _make_nested_calendar(depth)
    cal = Calendar.from_ical(ics)
    # Default recursion limit (1000) used to crash for depth >= ~498.
    result = repr(cal)
    assert result.startswith("VCALENDAR(")
    assert result.endswith(")")
    # Each nested VEVENT is reflected in the output.
    assert result.count("VEVENT(") == depth


def test_str_does_not_raise_recursion_error():
    """``str()`` (which falls through to ``__repr__``) must also be safe."""
    cal = Calendar.from_ical(_make_nested_calendar(800))
    result = str(cal)
    assert "VCALENDAR(" in result


def test_repr_format_unchanged_for_shallow_calendar():
    """Output format must match the previous recursive implementation
    for normally-shaped calendars."""
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//x//x//EN\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:a@example.com\r\n"
        "DTSTAMP:20260101T000000Z\r\n"
        "END:VEVENT\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:b@example.com\r\n"
        "DTSTAMP:20260101T000000Z\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    cal = Calendar.from_ical(ics)
    r = repr(cal)
    # Two siblings, comma-separated, both reachable in the output.
    assert r.count("VEVENT(") == 2
    assert "a@example.com" in r
    assert "b@example.com" in r
    # General shape: VCALENDAR({...}, VEVENT({...}), VEVENT({...}))
    assert r.startswith("VCALENDAR(")
    assert r.endswith(")")
