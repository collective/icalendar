"""Behavioral tests for :class:`~icalendar.cal.lazy.LazyCalendar`.

Tests here cover serialization round-trips, property accessors, timezone
handling, and ``with_uid()`` edge cases not covered by
:mod:`test_issue_1050_lazy_parsing`.

See :issue:`1050`.
"""

from datetime import datetime

import pytest

from icalendar import Calendar, Event


def test_empty_calendar_has_no_subcomponents(lazy_calendars):
    """An empty calendar has no subcomponents after accessing them."""
    cal = lazy_calendars.issue_1050_empty_calendar

    assert len(cal.subcomponents) == 0
    assert not cal.is_lazy()


def test_timezone_only_calendar_stays_lazy(lazy_calendars):
    """A calendar with only ``VTIMEZONE`` stays lazy after accessing timezones."""
    cal = lazy_calendars.issue_1050_timezone_only_calendar

    assert cal.is_lazy()
    timezones = cal.walk("VTIMEZONE")
    assert len(timezones) == 1
    assert cal.is_lazy()


@pytest.mark.parametrize(
    ("prop", "summary"),
    [
        ("todos", "Test Todo 1"),
        ("journals", "Test Journal 1"),
    ],
)
def test_component_property(calendars, prop, summary):
    """Accessing ``.todos`` and ``.journals`` returns the correct components."""
    cal = calendars.issue_1050_calendar_with_events_and_todos

    components = getattr(cal, prop)
    assert len(components) == 1
    assert str(components[0]["SUMMARY"]) == summary


def test_tzid_accessible_on_events(calendars):
    """Events carry their ``TZID`` parameter after parsing."""
    cal = calendars.issue_1050_calendar_with_events_and_todos

    assert cal.events[0]["DTSTART"].params.get("TZID") == "America/New_York"


def test_property_and_walk_access(calendars):
    """Mixing property access and ``walk()`` in any order returns correct counts."""
    cal = calendars.issue_1050_calendar_with_events_and_todos

    assert len(cal.journals) == 1
    assert len(cal.events) == 2
    assert len(cal.walk("VTODO")) == 1
    assert len(cal.todos) == 1
    assert len(cal.events) == 2


def test_forward_timezone_reference(calendars):
    """``VTIMEZONE`` defined after its referencing event is still resolved."""
    cal = calendars.issue_1050_forward_timezone_reference

    assert len(cal.events) == 1
    dtstart = cal.events[0]["DTSTART"].dt
    assert dtstart.tzinfo is not None
    assert str(dtstart.tzinfo) == "Europe/Berlin"


@pytest.mark.parametrize("access", ["none", "partial", "full"])
def test_to_ical_roundtrip(calendars, access):
    """Serializing at any parse state preserves all component counts."""
    cal = calendars.issue_1050_calendar_with_events_and_todos

    if access == "partial":
        _ = cal.events
    elif access == "full":
        _ = cal.walk()

    output = cal.to_ical()
    cal2 = Calendar.from_ical(output)
    assert len(cal2.walk("VEVENT")) == 2
    assert len(cal2.walk("VTODO")) == 1
    assert len(cal2.walk("VJOURNAL")) == 1
    assert len(cal2.walk("VTIMEZONE")) == 1


def test_add_component_appears_in_events(calendars):
    """``add_component()`` appends to the parsed event list."""
    cal = calendars.issue_1050_simple_calendar

    new_event = Event()
    new_event.add("UID", "new-event@example.com")
    new_event.add("SUMMARY", "New Event")
    new_event.add("DTSTART", datetime(2025, 2, 1, 10, 0, 0))
    cal.add_component(new_event)

    uids = sorted(str(e["UID"]) for e in cal.events)
    assert uids == ["new-event@example.com", "simple-event@example.com"]


def test_multiple_calendars(calendars):
    """``from_ical(..., multiple=True)`` returns all calendars."""
    cals = calendars.multiple.issue_1050_multiple_calendars

    assert len(cals) == 2
    assert len(cals[0].events) == 1
    assert len(cals[1].events) == 1


def test_uid_substring_in_description(calendars):
    """``with_uid()`` returns only the component whose ``UID`` matches exactly.

    :class:`~icalendar.parser.ical.lazy.LazySubcomponent` scans raw lines to
    decide whether to parse a component for ``with_uid()``. A ``DESCRIPTION``
    that contains the target UID string causes that component to be parsed as a
    false positive — this is intentional (parse more, never miss) — but the
    returned list must contain only the exact match.
    """
    cal = calendars.issue_1050_uid_in_description

    result = cal.with_uid("abc")
    assert len(result) == 1
    assert result[0]["SUMMARY"] == "target"
