"""Test the boundary between calendar data and file paths in ``from_ical``.

A newline-free string passed to :meth:`Component.from_ical` is probed as a
file path, while strings containing line breaks (i.e. real iCalendar data) are
never read from disk. These tests pin down that boundary:

* valid calendar data never touches the filesystem,
* non-existent / invalid string paths raise a consistent ``ValueError``
  (never ``OSError``) on every platform,
* a missing :class:`pathlib.Path` raises ``FileNotFoundError`` like
  :meth:`pathlib.Path.read_bytes`.

See issue: https://github.com/collective/icalendar/issues/1436
Related: https://github.com/collective/icalendar/issues/756
"""

from pathlib import Path

import pytest

from icalendar import Calendar
from icalendar.cal.examples import get_example


def test_valid_calendar_string_never_touches_the_filesystem(monkeypatch):
    """Parsing real calendar data must not probe or read any file."""
    cal_bytes = get_example("calendars", "example")
    cal_string = cal_bytes.decode()
    expected = Calendar.from_ical(cal_bytes).to_ical()

    def fail(*args, **kwargs):
        raise AssertionError("from_ical accessed the filesystem for calendar data")

    monkeypatch.setattr(Path, "is_file", fail)
    monkeypatch.setattr(Path, "read_bytes", fail)

    calendar = Calendar.from_ical(cal_string)

    assert calendar.to_ical() == expected


def test_nonexistent_string_path_raises_value_error(tmp_path):
    """A newline-free string that is not a file is parsed as (invalid) data."""
    missing = str(tmp_path / "does-not-exist.ics")

    with pytest.raises(ValueError):
        Calendar.from_ical(missing)


@pytest.mark.parametrize(
    "bad_string",
    [
        "not a calendar",
        "embedded\0null",  # rejected by the OS as a path -> ValueError, not OSError
        "x" * 100_000,  # too long to be a path on every platform
    ],
    ids=["plain-text", "null-byte", "too-long"],
)
def test_invalid_string_paths_raise_value_error_not_os_error(bad_string):
    """Invalid path strings must surface a consistent ValueError on all OSes."""
    with pytest.raises(ValueError):
        Calendar.from_ical(bad_string)


def test_missing_path_object_raises_file_not_found(tmp_path):
    """A ``Path`` is always treated as a path: missing files raise clearly."""
    missing = tmp_path / "does-not-exist.ics"

    with pytest.raises(FileNotFoundError):
        Calendar.from_ical(missing)
