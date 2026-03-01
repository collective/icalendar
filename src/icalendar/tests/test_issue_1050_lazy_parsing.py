"""Test lazy parsing of calendar components.

See https://github.com/collective/icalendar/issues/1050
"""

from typing import TYPE_CHECKING

import pytest

from icalendar import Alarm, Event, LazyCalendar
from icalendar.parser.ical.lazy import LazySubcomponent

if TYPE_CHECKING:
    from calendar import Calendar


def assert_is_lazy_calendar(calendar: LazyCalendar) -> None:
    """Assert that the calendar is a lazy calendar."""
    assert isinstance(calendar, LazyCalendar)
    assert calendar._subcomponents.is_lazy()
    assert calendar.is_lazy()


def assert_is_parsed_calendar(calendar: LazyCalendar) -> None:
    """Assert that the calendar is a parsed calendar."""
    assert isinstance(calendar, LazyCalendar)
    assert not calendar._subcomponents.is_lazy()
    assert not calendar.is_lazy()


class MockParser:
    def __init__(self, component):
        self._component = component
        self._calls = 0

    def parse(self):
        """Return the component."""
        self._calls += 1
        return [self._component]


@pytest.fixture
def mock_parser():
    """A mock parser that returns a fixed component."""
    return MockParser("mock_component")


@pytest.fixture
def lazy_subcomponent(mock_parser):
    """A lazy subcomponent that uses the mock parser."""
    return LazySubcomponent("VEVENT", mock_parser)


def test_lazy_subcomponent_is_not_parsed_when_created(mock_parser, lazy_subcomponent):
    """The component is inisially not parsed."""
    assert not lazy_subcomponent.is_parsed()
    assert lazy_subcomponent._parser is mock_parser
    assert mock_parser._calls == 0


def test_lazy_subcomponent_returns_component(lazy_subcomponent, mock_parser):
    """We retrieve the component inside."""
    component = lazy_subcomponent.parse()
    assert component == "mock_component"
    assert mock_parser._calls == 1
    assert lazy_subcomponent.is_parsed()


def test_parsing_twice_returns_same_component(lazy_subcomponent, mock_parser):
    """Parsing twice returns the same component."""
    component1 = lazy_subcomponent.parse()
    component2 = lazy_subcomponent.parse()
    assert component1 is component2
    assert mock_parser._calls == 1


def test_when_parsed_parser_is_freed(lazy_subcomponent, mock_parser):
    """Test that we can remove references to the content lines."""
    component = lazy_subcomponent.parse()
    assert component == "mock_component"
    assert lazy_subcomponent._parser is None


def test_big_calendar_returns_a_calendar(lazy_calendars):
    """Test that the BigCalendar returns a Calendar."""
    assert isinstance(lazy_calendars.empty, LazyCalendar)


@pytest.mark.parametrize(
    "component_name", ["VEVENT", "VTODO", "VALARM", "X-COMPONENT", "VTIMEZONE"]
)
def test_can_only_parse_calendar_components(component_name):
    """Test that we still get a component even if the string contains other components."""
    component = LazyCalendar.from_ical(f"BEGIN:{component_name}\nEND:{component_name}")
    assert component.name == component_name
    assert not component.is_lazy()


def test_big_calendar_is_initially_lazy(lazy_calendars):
    """Test that the BigCalendar is initially lazy."""
    calendar = lazy_calendars.example
    assert_is_lazy_calendar(calendar)


def test_adding_a_component_to_a_lazy_calendar(lazy_calendars):
    """Test that we can add a component to a lazy calendar."""
    calendar: LazyCalendar = lazy_calendars.empty
    calendar.add_component(Event())
    assert_is_lazy_calendar(calendar)


def test_getting_the_subcomponents_of_a_lazy_calendar(lazy_calendars, calendars):
    """Test that we can get the subcomponents of a lazy calendar."""
    calendar: LazyCalendar = lazy_calendars.example
    subcomponents = calendar.subcomponents
    assert len(subcomponents) == 3
    assert_is_parsed_calendar(calendar)
    assert calendars.example.subcomponents == subcomponents


def test_parsing_a_lazy_calendar_twice(lazy_calendars):
    """Test that parsing a lazy calendar twice does not change the result."""
    calendar: LazyCalendar = lazy_calendars.example
    subcomponents1 = calendar.subcomponents
    subcomponents2 = calendar.subcomponents
    assert subcomponents1 is subcomponents2
    assert_is_parsed_calendar(calendar)


name2getter = {
    "VTIMEZONE": "timezones",
    "VEVENT": "events",
    "VTODO": "todos",
    "VJOURNAL": "journals",
    "VAVAILABILITY": "availabilities",
}


@pytest.mark.parametrize("walk", [True, False])
@pytest.mark.parametrize(
    ("name", "parsed"),
    [
        ("VTIMEZONE", ("VTIMEZONE",)),
        ("VEVENT", ("VTIMEZONE", "VEVENT")),
        ("VTODO", ("VTIMEZONE", "VTODO")),
        ("VJOURNAL", ("VTIMEZONE", "VJOURNAL")),
        ("VAVAILABILITY", ("VTIMEZONE", "VAVAILABILITY")),
    ],
)
@pytest.mark.parametrize("fully_parsed", [True, False])
def test_accessing_timezones(walk, calendars, name, parsed, fully_parsed):
    """Check that only timezones are parsed.

    Skipping FREEBUSY for now is ok as they are for requests and need the whole calendar anyway.
    """
    calendar: Calendar = calendars.issue_1050_all_components
    if fully_parsed:
        calendar.subcomponents
    components = calendar.walk(name) if walk else getattr(calendar, name2getter[name])
    assert len(components) == 1, (
        "We only have one component of each type in the calendar."
    )
    assert components[0].name == name
    if isinstance(calendar, LazyCalendar) and not fully_parsed:
        assert_only_parsed(calendar, parsed)


def assert_only_parsed(calendar, parsed):
    """Check that only certain types of components are parsed"""
    assert calendar.is_lazy(), "The calendar should not be fully parsed."
    parsed_in_calendar = {
        lc.name for lc in calendar._subcomponents._components if lc.is_parsed()
    }
    assert parsed_in_calendar == set(parsed), (
        f"We expect only {', '.join(parsed)} to be parsed, not {', '.join(parsed_in_calendar)}."
    )


def test_walk_parses_the_whole_calendar(calendars):
    """Walk goes through them all."""
    calendar = calendars.issue_1050_all_components
    components = calendar.walk()
    assert len(components) == 9
    assert not calendar.is_lazy()


def test_walk_and_find_an_alarm(calendars):
    """Walking and finding the alarm inside."""
    alarms: list[Alarm] = calendars.issue_1050_all_components.walk("VALARM")
    assert len(alarms) == 1
    alarm = alarms[0]
    assert alarm.name == "VALARM"


@pytest.mark.parametrize(
    ("uid", "parsed"),
    [
        ("event-1", ("VTIMEZONE", "VEVENT")),
        ("calendar-1", ("VTIMEZONE",)),
        ("todo-1", ("VTIMEZONE", "VTODO")),
        ("journal-1", ("VTIMEZONE", "VJOURNAL")),
        ("availability-1", ("VTIMEZONE", "VAVAILABILITY")),
        ("alarm-1", ("VTIMEZONE", "VEVENT")),
    ],
)
@pytest.mark.parametrize("fully_parsed", [True, False])
def test_get_with_uid(calendars, uid, parsed, fully_parsed):
    calendar = calendars.issue_1050_all_components
    if fully_parsed:
        calendar.subcomponents
    components = calendar.with_uid(uid)
    assert len(components) == 1
    assert components[0].uid == uid
    if isinstance(calendar, LazyCalendar) and not fully_parsed:
        assert_only_parsed(calendar, parsed)


def test_absent_uid(calendars):
    calendar = calendars.issue_1050_all_components
    components = calendar.with_uid("non-existent-uid")
    assert len(components) == 0
