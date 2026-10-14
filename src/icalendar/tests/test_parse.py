"""Tests for the top-level parse convenience function."""

from pathlib import Path

import pytest

from icalendar import parse
from icalendar.error import InvalidCalendar


def test_parse_ical_bytes():
    ical = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//EN
END:VCALENDAR"""
    cal = parse(ical)
    assert cal.version == "2.0"
    assert cal.prodid == "-//Test//EN"


def test_parse_ical_multiple():
    ical = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//EN
END:VCALENDAR"""
    cals = parse(ical, multiple=True)
    assert isinstance(cals, list)
    assert len(cals) == 1


def test_parse_jcal():
    jcal = '["vcalendar",[["version",{},"text","2.0"],["prodid",{},"text","-//Test//EN"]],[]]'
    cal = parse(jcal)
    assert cal.version == "2.0"


def test_parse_empty_raises():
    with pytest.raises(InvalidCalendar):
        parse(b"")


def test_parse_unknown_format_raises():
    with pytest.raises(InvalidCalendar):
        parse(b"not a calendar")


def test_parse_from_path(tmp_path: Path):
    path = tmp_path / "test.ics"
    path.write_bytes(
        b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Path//EN
END:VCALENDAR"""
    )
    cal = parse(path)
    assert cal.prodid == "-//Path//EN"
