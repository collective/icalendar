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

from icalendar import Calendar, Event


def _make_nested_calendar(depth: int) -> str:
    """Return an .ics payload with ``depth`` levels of nested VEVENT."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//test//test//EN"]
    lines += ["BEGIN:VEVENT"] * depth
    lines += ["UID:nested@example.com", "DTSTAMP:20260101T000000Z"]
    lines += ["END:VEVENT"] * depth
    lines += ["END:VCALENDAR"]
    return "\r\n".join(lines) + "\r\n"


@pytest.mark.parametrize("depth", [10, 100, 500, 1000])
@pytest.mark.parametrize("fn", [repr, str], ids=["repr", "str"])
def test_repr_and_str_do_not_raise_recursion_error(fn, depth):
    """``repr()`` and ``str()`` must not raise ``RecursionError``
    regardless of nesting depth. ``str()`` falls through to ``__repr__``,
    so the same depths are exercised for both.
    """
    ics = _make_nested_calendar(depth)
    cal = Calendar.from_ical(ics)
    # Default recursion limit (1000) used to crash for depth >= ~498.
    result = fn(cal)
    assert result.startswith("VCALENDAR(")
    assert result.endswith(")")
    # Each nested VEVENT is reflected in the output.
    assert result.count("VEVENT(") == depth


@pytest.mark.parametrize("depth", [1, 2, 10, 500, 1000])
def test_repr_exact_output_for_nested_components(depth):
    """The exact ``repr()`` string matches the format produced by the
    previous (recursive) implementation: ``VCALENDAR({}, VEVENT({}, ...))``.

    Built from empty :class:`Component` instances so the expected output
    can be spelled out exactly without depending on the ``repr`` of any
    parsed property value.
    """
    cal = Calendar()
    parent = cal
    for _ in range(depth):
        child = Event()
        parent.add_component(child)
        parent = child
    expected = "VCALENDAR({}" + ", VEVENT({}" * depth + ")" * (depth + 1)
    assert repr(cal) == expected


def test_repr_exact_output_for_sibling_components():
    """The exact ``repr()`` string for sibling subcomponents matches the
    previous recursive format: ``VCALENDAR({}, VEVENT({}), VEVENT({}))``.
    """
    cal = Calendar()
    cal.add_component(Event())
    cal.add_component(Event())
    assert repr(cal) == "VCALENDAR({}, VEVENT({}), VEVENT({}))"
