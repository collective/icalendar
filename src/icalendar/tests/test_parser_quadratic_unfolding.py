"""Regression tests for the quadratic unfolding/whitespace stripping in the
content line parser.

Both ``Contentline`` unfolding and ``_strip_ows_around_delimiters`` used regexes
whose greedy run was re-tried at every position of a long run, so a small but
adversarial calendar made parsing take seconds. The patched regexes match the
same strings in linear time.
"""

import time

import pytest

from icalendar import Calendar
from icalendar.parser.content_line import (
    Contentline,
    _strip_ows_around_delimiters,
)


def test_unfolding_preserves_behaviour():
    assert str(Contentline.from_ical("DESCRIPTION:Hello\r\n World")) == (
        "DESCRIPTION:HelloWorld"
    )
    # a run of blank lines before the continuation collapses, as before
    assert str(Contentline.from_ical("A:b\r\n\r\n c")) == "A:bc"


def test_strip_ows_around_adjacent_delimiters():
    assert _strip_ows_around_delimiters("X ; ; Y") == "X;;Y"
    assert _strip_ows_around_delimiters("VALUE  =  TEXT") == "VALUE=TEXT"


@pytest.mark.parametrize("payload", ["\n" * 200_000, " " * 200_000])
def test_pathological_input_parses_quickly(payload):
    if payload.startswith("\n"):
        ics = "BEGIN:VCALENDAR\r\n" + payload + "END:VCALENDAR\r\n"
    else:
        ics = (
            "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nX;" + payload + ":v\r\nEND:VCALENDAR\r\n"
        )
    start = time.perf_counter()
    Calendar.from_ical(ics)
    # the unpatched regexes need minutes for this input; the bound is generous
    # enough to never flake on slow CI while still catching a return of the
    # quadratic behaviour.
    assert time.perf_counter() - start < 5
