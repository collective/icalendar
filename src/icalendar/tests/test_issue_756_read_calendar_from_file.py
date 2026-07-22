"""Test reading a calendar from a file.

See issue: https://github.com/collective/icalendar/issues/756
"""

from pathlib import Path

import pytest

from icalendar import Calendar
from icalendar.cal.examples import get_example


@pytest.fixture
def dummy_cal(tmp_path: Path) -> tuple[Calendar, Path]:
    cal_path = tmp_path / "calendar.ics"
    cal_bytes = get_example("calendars", "example")
    cal_path.write_bytes(cal_bytes)

    return Calendar.from_ical(cal_bytes), cal_path


def test_reading_cal_from_path(dummy_cal):
    """Test reading a calendar from a valid path."""
    expected_cal, path = dummy_cal
    actual_cal = Calendar.from_ical(path)

    assert actual_cal.to_ical() == expected_cal.to_ical()


def test_existing_calendar_path_as_string_is_not_read(dummy_cal):
    """A string that matches an existing calendar file is parsed as data, not read.

    The path points at a real, parseable calendar file. If the string were still
    probed as a path, this call would read the file and return that calendar. It
    now parses the path string itself as iCalendar data, which fails.
    """
    _, path = dummy_cal

    with pytest.raises(ValueError):
        Calendar.from_ical(str(path))


def test_nonexistent_path_as_string_raises_parse_error(tmp_path: Path):
    """A path-like string that does not exist is parsed as data, not opened.

    A non-existent path must not raise ``FileNotFoundError`` (which would mean the
    parser tried to open it); it is parsed as data and raises a ``ValueError``.
    """
    missing = str(tmp_path / "does-not-exist.ics")

    with pytest.raises(ValueError):
        Calendar.from_ical(missing)


def test_reading_cal_from_long_string(dummy_cal):
    """Test reading a calendar from a long string (without path-too-long error)."""
    expected_cal, _ = dummy_cal
    expected_cal["key"] = "longvalue" * 1000
    long_string = expected_cal.to_ical().decode()
    actual_cal = Calendar.from_ical(long_string)

    assert actual_cal.to_ical() == expected_cal.to_ical()


def test_calendar_from_ical_is_declared_for_api_documentation():
    """Test Calendar.from_ical is documented as a Calendar API method."""
    cal_bytes = get_example("calendars", "example")

    assert "from_ical" in Calendar.__dict__
    assert (
        Calendar.from_ical(cal_bytes).to_ical()
        == Calendar.from_ical(cal_bytes).to_ical()
    )
