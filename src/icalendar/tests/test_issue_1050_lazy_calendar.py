"""Tests for LazyCalendar behavioral coverage not in test_issue_1050_lazy_parsing.py.

See :issue:`1050`.
"""

from datetime import datetime
from pathlib import Path

from icalendar import Calendar, Event, LazyCalendar

CALENDARS_FOLDER = Path(__file__).parent / "calendars"


def load_calendar(filename):
    return (CALENDARS_FOLDER / filename).read_bytes()


CALENDAR_WITH_EVENTS_AND_TODOS = load_calendar(
    "issue_1050_calendar_with_events_and_todos.ics"
)
SIMPLE_CALENDAR = load_calendar("issue_1050_simple_calendar.ics")
TIMEZONE_ONLY_CALENDAR = load_calendar("issue_1050_timezone_only_calendar.ics")
EMPTY_CALENDAR = load_calendar("issue_1050_empty_calendar.ics")
FORWARD_REF_CALENDAR = load_calendar("issue_1050_forward_timezone_reference.ics")
MULTI_CAL = load_calendar("issue_1050_multiple_calendars.ics")


def test_empty_calendar():
    """Empty calendar has no subcomponents and is not lazy."""
    cal = LazyCalendar.from_ical(EMPTY_CALENDAR)

    assert str(cal["VERSION"]) == "2.0"
    assert len(cal.subcomponents) == 0
    assert not cal.is_lazy()


def test_timezone_only_calendar_stays_lazy():
    """Calendar with only VTIMEZONE stays lazy until subcomponents are accessed."""
    cal = LazyCalendar.from_ical(TIMEZONE_ONLY_CALENDAR)

    assert cal.is_lazy()
    timezones = cal.walk("VTIMEZONE")
    assert len(timezones) == 1
    assert cal.is_lazy()


def test_todos_property():
    """Accessing .todos parses and returns todo components."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    todos = cal.todos
    assert len(todos) == 1
    assert str(todos[0]["SUMMARY"]) == "Test Todo 1"


def test_journals_property():
    """Accessing .journals returns journal components."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    journals = cal.journals
    assert len(journals) == 1
    assert str(journals[0]["SUMMARY"]) == "Test Journal 1"


def test_to_ical_before_access():
    """to_ical() produces correct output without prior property access."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    ical_output = cal.to_ical()

    assert b"BEGIN:VCALENDAR" in ical_output
    assert b"END:VCALENDAR" in ical_output
    assert b"BEGIN:VTIMEZONE" in ical_output
    assert b"BEGIN:VEVENT" in ical_output
    assert b"BEGIN:VTODO" in ical_output
    assert b"BEGIN:VJOURNAL" in ical_output


def test_to_ical_after_partial_access():
    """to_ical() produces correct output after accessing only some component types."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    _ = cal.events
    ical_output = cal.to_ical()

    assert b"BEGIN:VTIMEZONE" in ical_output
    assert b"BEGIN:VEVENT" in ical_output
    assert b"BEGIN:VTODO" in ical_output


def test_round_trip_preserves_component_counts():
    """Full round-trip parse → access → serialize → re-parse preserves component counts."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    _ = cal.walk()
    ical_output = cal.to_ical()

    cal2 = Calendar.from_ical(ical_output)
    assert len(cal2.walk("VEVENT")) == 2
    assert len(cal2.walk("VTODO")) == 1
    assert len(cal2.walk("VJOURNAL")) == 1
    assert len(cal2.walk("VTIMEZONE")) == 1


def test_round_trip_without_access():
    """Serializing without accessing lazy components preserves all data."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    ical_output = cal.to_ical()

    cal2 = Calendar.from_ical(ical_output)
    assert len(cal2.walk("VEVENT")) == 2
    assert len(cal2.walk("VTODO")) == 1


def test_tzid_accessible_on_lazy_events():
    """VTIMEZONE is available when lazy events are parsed."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    event = cal.events[0]
    assert event["DTSTART"].params.get("TZID") == "America/New_York"


def test_forward_timezone_reference():
    """VTIMEZONE defined after events in the file is still resolved correctly."""
    cal = LazyCalendar.from_ical(FORWARD_REF_CALENDAR)

    assert len(cal.events) == 1
    dtstart = cal.events[0]["DTSTART"].dt
    assert dtstart.tzinfo is not None
    assert str(dtstart.tzinfo) == "Europe/Berlin"


def test_add_component_appears_in_events():
    """add_component() appends to the parsed event list."""
    cal = LazyCalendar.from_ical(SIMPLE_CALENDAR)

    new_event = Event()
    new_event.add("UID", "new-event@example.com")
    new_event.add("SUMMARY", "New Event")
    new_event.add("DTSTART", datetime(2025, 2, 1, 10, 0, 0))
    cal.add_component(new_event)

    uids = sorted(str(e["UID"]) for e in cal.events)
    assert uids == ["new-event@example.com", "simple-event@example.com"]


def test_multiple_calendars():
    """from_ical(..., multiple=True) returns all calendars."""
    cals = LazyCalendar.from_ical(MULTI_CAL, multiple=True)
    assert len(cals) == 2
    assert len(cals[0].events) == 1
    assert len(cals[1].events) == 1


def test_sequential_property_access():
    """Accessing different component type properties in sequence returns correct results."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    assert len(cal.journals) == 1
    assert len(cal.events) == 2
    assert len(cal.todos) == 1
    assert len(cal.events) == 2


def test_mixed_property_and_walk_access():
    """Mixing property access and walk() returns correct results."""
    cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

    assert len(cal.events) == 2
    assert len(cal.walk("VTODO")) == 1
    assert len(cal.journals) == 1
    assert len(cal.todos) == 1


def test_contains_uid_substring_match_parses_more():
    """with_uid() may parse components whose content contains the UID as a substring.

    :class:`~icalendar.parser.ical.component.ComponentIcalParser` does a substring
    scan of raw lines to decide whether to parse a component for ``with_uid()``.
    A DESCRIPTION that happens to contain the UID string causes that component
    to be parsed even though it is not the target. This is intentional: parse more,
    never miss.
    """
    ics = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"
        b"BEGIN:VEVENT\r\nUID:abc\r\nSUMMARY:target\r\nEND:VEVENT\r\n"
        b"BEGIN:VEVENT\r\nUID:xyz\r\nDESCRIPTION:contains abc in text\r\nEND:VEVENT\r\n"
        b"END:VCALENDAR\r\n"
    )
    cal = LazyCalendar.from_ical(ics)
    result = cal.with_uid("abc")
    assert len(result) == 1
    assert result[0]["SUMMARY"] == "target"
