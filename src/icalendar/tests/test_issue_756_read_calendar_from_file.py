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


def test_string_path_is_parsed_as_calendar_data(dummy_cal):
    """Test that string input is not interpreted as a filesystem path."""
    _, path = dummy_cal

    with pytest.raises(ValueError) as exc_info:
        Calendar.from_ical(str(path))

    assert "BEGIN:VCALENDAR" not in str(exc_info.value)


def test_string_path_does_not_disclose_file_contents(tmp_path: Path):
    """Test that parsing a string path does not read from the filesystem."""
    path = tmp_path / "secret.txt"
    path.write_text("SECRET-CONTENT-WITHOUT-NEWLINE", encoding="utf-8")

    with pytest.raises(ValueError) as exc_info:
        Calendar.from_ical(str(path))

    assert "SECRET-CONTENT-WITHOUT-NEWLINE" not in str(exc_info.value)


def test_reading_cal_from_long_string(dummy_cal):
    """Test reading a calendar from a long string (without path-too-long error)."""
    expected_cal, _ = dummy_cal
    expected_cal["key"] = "longvalue" * 1000
    long_string = expected_cal.to_ical().decode()
    actual_cal = Calendar.from_ical(long_string)

    assert actual_cal.to_ical() == expected_cal.to_ical()
