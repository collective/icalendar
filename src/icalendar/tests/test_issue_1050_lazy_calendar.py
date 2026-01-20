"""Tests for LazyCalendar - lazy subcomponent parsing for large calendars.

See https://github.com/collective/icalendar/issues/1050
"""

from pathlib import Path

from icalendar import Calendar, LazyCalendar

# Path to test data
CALENDARS_FOLDER = Path(__file__).parent / "calendars"


def load_calendar(filename):
    """Load a calendar file from the calendars folder."""
    return (CALENDARS_FOLDER / filename).read_bytes()


CALENDAR_WITH_EVENTS_AND_TODOS = load_calendar(
    "issue_1050_calendar_with_events_and_todos.ics"
)
SIMPLE_CALENDAR = load_calendar("issue_1050_simple_calendar.ics")
TIMEZONE_ONLY_CALENDAR = load_calendar("issue_1050_timezone_only_calendar.ics")
EMPTY_CALENDAR = load_calendar("issue_1050_empty_calendar.ics")
FORWARD_REF_CALENDAR = load_calendar("issue_1050_forward_timezone_reference.ics")
MULTI_CAL = load_calendar("issue_1050_multiple_calendars.ics")


class TestLazyCalendarBasicParsing:
    """Test basic parsing functionality."""

    def test_lazy_calendar_parses_properties_eagerly(self):
        """Calendar properties (VERSION, PRODID) are accessible immediately."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Properties should be available without triggering lazy parsing
        assert str(cal["VERSION"]) == "2.0"
        assert "-//Test//Test//EN" in str(cal["PRODID"])

        # No events should be parsed yet
        assert len(cal._parsed_indices) == 0

    def test_lazy_calendar_parses_vtimezone_eagerly(self):
        """VTIMEZONE components are parsed immediately and in subcomponents."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # VTIMEZONE should be in subcomponents
        assert len(cal.subcomponents) == 1
        assert cal.subcomponents[0].name == "VTIMEZONE"
        assert cal.subcomponents[0]["TZID"] == "America/New_York"

        # Events should not be parsed yet
        assert len(cal._parsed_indices) == 0

    def test_lazy_calendar_defers_vevent_parsing(self):
        """VEVENT components are not in subcomponents until accessed."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Should have raw components stored
        assert len(cal._raw_components) == 4  # 2 events, 1 todo, 1 journal

        # Check component types in raw storage
        raw_types = [name for name, _ in cal._raw_components]
        assert raw_types.count("VEVENT") == 2
        assert raw_types.count("VTODO") == 1
        assert raw_types.count("VJOURNAL") == 1

        # Only VTIMEZONE in subcomponents
        assert len(cal.subcomponents) == 1

    def test_lazy_calendar_empty(self):
        """Empty calendar works correctly."""
        cal = LazyCalendar.from_ical(EMPTY_CALENDAR)

        assert str(cal["VERSION"]) == "2.0"
        assert len(cal.subcomponents) == 0
        assert len(cal._raw_components) == 0

    def test_lazy_calendar_only_timezones(self):
        """Calendar with only VTIMEZONE has no lazy components."""
        cal = LazyCalendar.from_ical(TIMEZONE_ONLY_CALENDAR)

        assert len(cal.subcomponents) == 1
        assert cal.subcomponents[0].name == "VTIMEZONE"
        assert len(cal._raw_components) == 0


class TestLazyCalendarAccess:
    """Test lazy component access triggers parsing."""

    def test_events_property_triggers_parsing(self):
        """Accessing .events parses and returns events."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Before access
        assert len(cal._parsed_indices) == 0

        # Access events
        events = cal.events
        assert len(events) == 2

        # Events should now be parsed
        assert len(cal._parsed_indices) == 2  # Only VEVENT parsed

        # Check event details
        summaries = sorted(str(e["SUMMARY"]) for e in events)
        assert summaries == ["Test Event 1", "Test Event 2"]

    def test_todos_property_triggers_parsing(self):
        """Accessing .todos parses and returns todos."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        todos = cal.todos
        assert len(todos) == 1
        assert str(todos[0]["SUMMARY"]) == "Test Todo 1"

        # Only VTODO should be parsed
        assert len(cal._parsed_indices) == 1

    def test_walk_with_name_triggers_selective_parsing(self):
        """walk(name) only parses components of that type."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Walk for events only
        events = cal.walk("VEVENT")
        assert len(events) == 2

        # Only events should be parsed
        assert len(cal._parsed_indices) == 2

        # Todos and journals still in raw storage
        unparsed = [
            name
            for i, (name, _) in enumerate(cal._raw_components)
            if i not in cal._parsed_indices
        ]
        assert "VTODO" in unparsed
        assert "VJOURNAL" in unparsed

    def test_walk_without_name_parses_all(self):
        """walk() without name parses all components."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Walk all
        all_components = cal.walk()

        # walk() returns all components recursively including nested ones:
        # Calendar, Timezone, STANDARD, DAYLIGHT, 2 Events, 1 Todo, 1 Journal = 8
        assert len(all_components) == 8

        # All raw components should be parsed
        assert len(cal._parsed_indices) == 4

    def test_multiple_accesses_return_same_objects(self):
        """Multiple accesses return the same parsed objects."""
        cal = LazyCalendar.from_ical(SIMPLE_CALENDAR)

        events1 = cal.events
        events2 = cal.events

        # Should be the same objects
        assert events1[0] is events2[0]


class TestLazyCalendarSerialization:
    """Test to_ical() produces correct output."""

    def test_to_ical_before_access(self):
        """to_ical() works correctly without accessing lazy components."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Serialize without accessing events
        ical_output = cal.to_ical()

        # Should contain all components
        assert b"BEGIN:VCALENDAR" in ical_output
        assert b"END:VCALENDAR" in ical_output
        assert b"BEGIN:VTIMEZONE" in ical_output
        assert b"BEGIN:VEVENT" in ical_output
        assert b"BEGIN:VTODO" in ical_output
        assert b"BEGIN:VJOURNAL" in ical_output

    def test_to_ical_after_access(self):
        """to_ical() works correctly after accessing lazy components."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Access events to trigger parsing
        _ = cal.events

        # Serialize
        ical_output = cal.to_ical()

        # Should still contain all components
        assert b"BEGIN:VCALENDAR" in ical_output
        assert b"BEGIN:VTIMEZONE" in ical_output
        assert b"BEGIN:VEVENT" in ical_output
        assert b"BEGIN:VTODO" in ical_output

    def test_round_trip_preserves_data(self):
        """Parsing and re-serializing preserves the data."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Full round trip - parse, access all, serialize, parse again
        _ = cal.walk()  # Parse all
        ical_output = cal.to_ical()

        # Parse with regular Calendar to verify
        cal2 = Calendar.from_ical(ical_output)

        assert len(cal2.walk("VEVENT")) == 2
        assert len(cal2.walk("VTODO")) == 1
        assert len(cal2.walk("VJOURNAL")) == 1
        assert len(cal2.walk("VTIMEZONE")) == 1

    def test_round_trip_without_access(self):
        """Round trip works even without accessing lazy components."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Serialize without accessing any lazy components
        ical_output = cal.to_ical()

        # Parse with regular Calendar
        cal2 = Calendar.from_ical(ical_output)

        assert len(cal2.walk("VEVENT")) == 2
        assert len(cal2.walk("VTODO")) == 1


class TestLazyCalendarTimezoneHandling:
    """Test timezone handling with lazy parsing."""

    def test_timezone_cached_for_lazy_events(self):
        """VTIMEZONE is cached and available for lazy event parsing."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Access events - should use cached timezone
        events = cal.events

        # Events should have proper timezone info
        event = events[0]
        dtstart = event["DTSTART"]
        assert dtstart.params.get("TZID") == "America/New_York"

    def test_forward_timezone_reference(self):
        """VTIMEZONE defined after events still works."""
        cal = LazyCalendar.from_ical(FORWARD_REF_CALENDAR)

        # VTIMEZONE should still be parsed eagerly (appears after VEVENT in file)
        # Note: Current implementation parses in order, so VEVENT is stored
        # as raw, then VTIMEZONE is parsed and cached

        # Access events
        events = cal.events
        assert len(events) == 1


class TestLazyCalendarVsRegularCalendar:
    """Compare LazyCalendar behavior to regular Calendar."""

    def test_same_events_as_regular_calendar(self):
        """LazyCalendar produces same events as regular Calendar."""
        lazy_cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)
        regular_cal = Calendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        lazy_events = lazy_cal.events
        regular_events = regular_cal.events

        assert len(lazy_events) == len(regular_events)

        for lazy_event, regular_event in zip(lazy_events, regular_events, strict=True):
            assert str(lazy_event["UID"]) == str(regular_event["UID"])
            assert str(lazy_event["SUMMARY"]) == str(regular_event["SUMMARY"])

    def test_same_timezones_as_regular_calendar(self):
        """LazyCalendar has same timezones as regular Calendar."""
        lazy_cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)
        regular_cal = Calendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        assert len(lazy_cal.timezones) == len(regular_cal.timezones)
        assert lazy_cal.timezones[0]["TZID"] == regular_cal.timezones[0]["TZID"]


class TestLazyCalendarAddComponent:
    """Test adding components to LazyCalendar."""

    def test_add_component_works(self):
        """Adding a component to LazyCalendar works correctly."""
        from datetime import datetime

        from icalendar import Event

        cal = LazyCalendar.from_ical(SIMPLE_CALENDAR)

        # Add a new event
        new_event = Event()
        new_event.add("UID", "new-event@example.com")
        new_event.add("SUMMARY", "New Event")
        new_event.add("DTSTART", datetime(2025, 2, 1, 10, 0, 0))

        cal.add_component(new_event)

        # Should be in subcomponents
        assert new_event in cal.subcomponents

        # Events should include both original and new
        events = cal.events
        assert len(events) == 2

        uids = sorted(str(e["UID"]) for e in events)
        assert uids == ["new-event@example.com", "simple-event@example.com"]


class TestLazyCalendarMultiple:
    """Test multiple calendar parsing."""

    def test_multiple_calendars(self):
        """Parsing multiple calendars works."""
        cals = LazyCalendar.from_ical(MULTI_CAL, multiple=True)
        assert len(cals) == 2

        # Each should have one event
        assert len(cals[0].events) == 1
        assert len(cals[1].events) == 1


class TestLazyCalendarJournals:
    """Test journal component access."""

    def test_journals_property(self):
        """Accessing journals works correctly."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        journals = cal.journals
        assert len(journals) == 1
        assert str(journals[0]["SUMMARY"]) == "Test Journal 1"


class TestLazyCalendarAccessPatterns:
    """Test different access patterns work correctly."""

    def test_access_events_then_todos(self):
        """Accessing events then todos works correctly."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        events = cal.events
        assert len(events) == 2

        todos = cal.todos
        assert len(todos) == 1

        # All should be accessible
        assert len(cal.events) == 2
        assert len(cal.todos) == 1

    def test_access_todos_then_events(self):
        """Accessing todos then events works correctly."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        todos = cal.todos
        assert len(todos) == 1

        events = cal.events
        assert len(events) == 2

    def test_access_journals_then_events_then_todos(self):
        """Accessing in journals -> events -> todos order works."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        journals = cal.journals
        assert len(journals) == 1

        events = cal.events
        assert len(events) == 2

        todos = cal.todos
        assert len(todos) == 1

    def test_access_mixed_with_walk(self):
        """Mixing property access with walk() works correctly."""
        cal = LazyCalendar.from_ical(CALENDAR_WITH_EVENTS_AND_TODOS)

        # Access events first
        events = cal.events
        assert len(events) == 2

        # Then walk for todos
        todos = cal.walk("VTODO")
        assert len(todos) == 1

        # Then use journals property
        journals = cal.journals
        assert len(journals) == 1

        # All should still work
        assert len(cal.events) == 2
        assert len(cal.todos) == 1
