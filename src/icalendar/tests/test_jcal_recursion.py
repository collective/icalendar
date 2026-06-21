"""Regression test for RecursionError on deeply-nested jCal.

The iCal parser/serializer was made iterative to survive deep nesting
(see https://github.com/collective/icalendar/issues/1370), but the jCal
counterparts :meth:`Component.from_jcal` and :meth:`Component.to_jcal`
remained recursive: a small jCal payload nesting components a few hundred
levels deep raised an uncaught ``RecursionError`` at the default recursion
limit (1000).

These tests mirror ``test_walk_handles_deeply_nested_components`` and use a
depth comfortably above the recursion limit so the recursive implementation
would fail while the iterative one succeeds.
"""

import sys

import pytest

from icalendar import Component
from icalendar.error import JCalParsingError


def _nested_jcal(depth: int) -> list:
    """Return a jCal VCALENDAR with ``depth`` levels of nested VEVENT."""
    root = [
        "vcalendar",
        [["version", {}, "text", "2.0"], ["prodid", {}, "text", "-//test//test//EN"]],
        [],
    ]
    inner = root
    for _ in range(depth):
        child = ["vevent", [["uid", {}, "text", "nested@example.com"]], []]
        inner[2].append(child)
        inner = child
    return root


def _nesting_depth(component: Component) -> int:
    """Count how many levels of single-child nesting ``component`` has."""
    depth = 0
    while component.subcomponents:
        depth += 1
        component = component.subcomponents[0]
    return depth


def test_from_jcal_handles_deeply_nested_components():
    """Deeply nested jCal must parse without exceeding the recursion limit."""
    depth = sys.getrecursionlimit() + 50
    calendar = Component.from_jcal(_nested_jcal(depth))
    assert calendar.name == "VCALENDAR"
    assert _nesting_depth(calendar) == depth


def test_to_jcal_handles_deeply_nested_components():
    """Serializing a deeply nested component must not recurse."""
    depth = sys.getrecursionlimit() + 50
    calendar = Component.from_jcal(_nested_jcal(depth))
    jcal = calendar.to_jcal()
    # Walk the produced jCal structure to confirm the full depth survived.
    node, levels = jcal, 0
    while node[2]:
        levels += 1
        node = node[2][0]
    assert levels == depth


def test_deeply_nested_jcal_round_trips():
    """from_jcal -> to_jcal -> from_jcal is stable at large depth."""
    depth = sys.getrecursionlimit() + 50
    jcal = _nested_jcal(depth)
    once = Component.from_jcal(jcal).to_jcal()
    twice = Component.from_jcal(once).to_jcal()
    # Compare by walking the chain: a plain ``once == twice`` would compare the
    # nested lists recursively and hit RecursionError at this depth, even though
    # producing them did not.
    a, b = once, twice
    levels = 0
    while True:
        # A jCal component is exactly [name, properties, subcomponents]; assert
        # the length so the element-by-element comparison cannot skip an entry.
        assert len(a) == 3
        assert len(b) == 3
        assert a[0] == b[0]  # component name
        assert a[1] == b[1]  # properties (a shallow list)
        if not a[2]:
            assert not b[2]
            break
        assert len(a[2]) == len(b[2]) == 1
        a, b = a[2][0], b[2][0]
        levels += 1
    assert levels == depth


def test_branching_jcal_round_trips():
    """to_jcal preserves sibling order in branching (non-linear) trees.

    The round-trip test above only exercises a single child per node. The
    iterative stack walk appends each child to its parent before pushing it,
    so sibling order must be independent of the LIFO pop order -- this locks
    that in with multiple siblings at two levels.
    """
    jcal = [
        "vcalendar",
        [["version", {}, "text", "2.0"], ["prodid", {}, "text", "-//test//EN"]],
        [
            [
                "vevent",
                [["uid", {}, "text", "first@test"]],
                [
                    [
                        "valarm",
                        [
                            ["action", {}, "text", "DISPLAY"],
                            ["description", {}, "text", "A"],
                            ["trigger", {}, "duration", "-PT15M"],
                        ],
                        [],
                    ],
                    [
                        "valarm",
                        [
                            ["action", {}, "text", "AUDIO"],
                            ["trigger", {}, "duration", "-PT5M"],
                        ],
                        [],
                    ],
                ],
            ],
            ["vevent", [["uid", {}, "text", "second@test"]], []],
        ],
    ]
    result = Component.from_jcal(jcal).to_jcal()
    # Sibling VEVENTs keep their order.
    assert result[2][0][1][0][3] == "first@test"
    assert result[2][1][1][0][3] == "second@test"
    # The first VEVENT keeps both of its VALARM subcomponents, in order.
    assert len(result[2][0][2]) == 2
    assert result[2][0][2][0][1][0][3] == "DISPLAY"
    assert result[2][0][2][1][1][0][3] == "AUDIO"


def test_error_path_is_preserved_for_nested_jcal():
    """Errors deep in the tree still report the accumulated jCal path."""
    # A malformed (non-list) subcomponent nested two levels deep.
    bad = [
        "vcalendar",
        [],
        [["vevent", [], [["valarm", [], [42]]]]],
    ]
    with pytest.raises(
        JCalParsingError,
        match=r"\[2\]\[0\]\[2\]\[0\]\[2\]\[0\] in Alarm: "
        r"A component must be a list with 3 items\.",
    ):
        Component.from_jcal(bad)
