"""Test JSON serialization of components."""

import json

import pytest

from icalendar.cal.calendar import Calendar
from icalendar.cal.component import Component
from icalendar.cal.event import Event


def test_apply_json_serialization():
    """Check that we can convert to JSON."""
    calendar = Calendar.new()
    calendar.add_component(Event())
    assert calendar.to_json() == json.dumps(calendar.to_jcal(), separators=(",", ":"))


MINIMAL_CALENDAR_JSON_PRETTY = """[
  "vcalendar",
  [
    [
      "version",
      {},
      "text",
      "2.0"
    ],
    [
      "prodid",
      {},
      "text",
      "-//collective//icalendar//7.3.1.dev270//EN"
    ],
    [
      "uid",
      {},
      "text",
      "664546b1-5828-49a9-adc5-80d108fb4f13"
    ]
  ],
  []
]"""


def test_pretty_json_also_works(calendars):
    cal: Calendar = calendars.minimal
    json_str = cal.to_json(indent=2)
    print(json_str)
    assert json_str == MINIMAL_CALENDAR_JSON_PRETTY


def test_invalid_indent_for_json(comp: Component):
    """Check that invalid arguments for indent raise a TypeError."""
    with pytest.raises(TypeError):
        comp.to_json(indent=3.14)  # type: ignore  # noqa: PGH003
    with pytest.raises(TypeError):
        comp.to_json(indent=object())  # type: ignore  # noqa: PGH003
