"""Test lazy parsing of calendar components.

See https://github.com/collective/icalendar/issues/1050
"""

import pytest

from icalendar import BigCalendar, Event
from icalendar.parser.ical.lazy import LazySubcomponent


def assert_is_lazy_calendar(calendar: BigCalendar) -> None:
    """Assert that the calendar is a lazy calendar."""
    assert isinstance(calendar, BigCalendar)
    assert calendar._subcomponents.is_lazy()


def assert_is_parsed_calendar(calendar: BigCalendar) -> None:
    """Assert that the calendar is a parsed calendar."""
    assert isinstance(calendar, BigCalendar)
    assert not calendar._subcomponents.is_lazy()


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


@pytest.mark.parametrize("component_name", ["VEVENT", "VTODO", "VALARM"])
def test_parse_into_lazy_component(component_name):
    """Test that these components are parsed into lazy components."""


def test_big_calendar_returns_a_calendar(big_calendars):
    """Test that the BigCalendar returns a Calendar."""
    assert isinstance(big_calendars.empty, BigCalendar)


@pytest.mark.parametrize(
    "component_name", ["VEVENT", "VTODO", "VALARM", "X-COMPONENT", "VTIMEZONE"]
)
def test_can_only_parse_calendar_components(component_name):
    """Test that we still get a component even if the string contains other components."""
    with pytest.raises(
        ValueError,
        match=rf"Expected VCALENDAR as root component but got {component_name}\.",
    ):
        BigCalendar.from_ical(f"BEGIN:{component_name}\nEND:{component_name}")


def test_big_calendar_is_initially_lazy(big_calendars):
    """Test that the BigCalendar is initially lazy."""
    calendar = big_calendars.example
    assert_is_lazy_calendar(calendar)


def test_adding_a_component_to_a_lazy_calendar(big_calendars):
    """Test that we can add a component to a lazy calendar."""
    calendar: BigCalendar = big_calendars.empty
    calendar.add_component(Event())
    assert_is_lazy_calendar(calendar)


def test_getting_the_subcomponents_of_a_lazy_calendar(big_calendars, calendars):
    """Test that we can get the subcomponents of a lazy calendar."""
    calendar: BigCalendar = big_calendars.example
    subcomponents = calendar.subcomponents
    assert len(subcomponents) == 3
    assert_is_parsed_calendar(calendar)
    assert calendars.example.subcomponents == subcomponents


def test_parsing_a_lazy_calendar_twice(big_calendars):
    """Test that parsing a lazy calendar twice does not change the result."""
    calendar: BigCalendar = big_calendars.example
    subcomponents1 = calendar.subcomponents
    subcomponents2 = calendar.subcomponents
    assert subcomponents1 is subcomponents2
    assert_is_parsed_calendar(calendar)
