import pytest
from datetime import datetime
from pathlib import Path
from icalendar import Calendar, Event, Todo, Journal


@pytest.fixture
def temp_path(tmp_path):
    """Create a temp directory and change to it for tests"""
    return tmp_path / "test.ics"


@pytest.fixture
def multiple_calendars_path():
    """Path to test file containing multiple calendar components"""
    return Path("src/icalendar/tests/calendars/multiple_calendar_components.ics")


def test_from_file_str_path(calendars):
    """Test reading from file using string path"""
    path = "src/icalendar/tests/calendars/example.ics"
    cal = Calendar.from_file(path)
    assert cal == calendars.example


def test_from_file_path_object(calendars):
    """Test reading from file using Path object"""
    path = Path("src/icalendar/tests/calendars/example.ics")
    cal = Calendar.from_file(path)
    assert cal == calendars.example


def test_from_file_multiple(multiple_calendars_path):
    """Test reading multiple components from a file"""
    cals = Calendar.from_file(multiple_calendars_path, multiple=True)
    assert isinstance(cals, list)
    assert len(cals) > 1
    assert all(isinstance(cal, Calendar) for cal in cals)


def test_from_file_non_existent():
    """Test attempting to read from non-existent file"""
    with pytest.raises(FileNotFoundError):
        Calendar.from_file("non_existent.ics")


def test_to_file_str_path(temp_path, calendars):
    """Test writing to file using string path"""
    cal = calendars.example
    cal.to_file(str(temp_path))
    assert temp_path.exists()
    # Verify contents by reading back
    cal2 = Calendar.from_file(temp_path)
    assert cal == cal2


def test_to_file_path_object(temp_path, calendars):
    """Test writing to file using Path object"""
    cal = calendars.example
    cal.to_file(temp_path)
    assert temp_path.exists()
    # Verify contents by reading back
    cal2 = Calendar.from_file(temp_path)
    assert cal == cal2


def test_other_components(temp_path):
    """Test file I/O with other component types"""
    components = [Event(), Todo(), Journal()]

    for comp in components:
        comp.add("summary", "Test")
        comp.to_file(temp_path)
        assert temp_path.exists()
        # Read back and verify it's the correct type
        comp2 = type(comp).from_file(temp_path)
        assert isinstance(comp2, type(comp))
        assert comp == comp2


def test_component_roundtrip(temp_path):
    """Test that a component survives a write/read cycle preserving all data"""
    # Create a complex calendar with nested components
    cal = Calendar()
    event = Event()
    event.add("summary", "Test Event")

    dt = datetime(2024, 1, 1, 12, 0, 0)
    event.add("dtstart", dt)
    cal.add_component(event)

    # Write and read back
    cal.to_file(temp_path)
    cal2 = Calendar.from_file(temp_path)

    # Verify equality
    assert cal == cal2
    assert len(cal2.subcomponents) == len(cal.subcomponents)
    assert cal2.subcomponents[0]["summary"] == "Test Event"
    assert cal2.subcomponents[0]["dtstart"].dt == dt
