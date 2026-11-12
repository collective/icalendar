from datetime import date, datetime, time, timedelta
from unittest.mock import Mock

import pytest

from icalendar.prop import vDate, vDatetime, vDDDTypes, vDuration, vTime


def test_instance():
    assert isinstance(vDDDTypes.from_ical("20010101T123000"), datetime)
    assert isinstance(vDDDTypes.from_ical("20010101"), date)


def test_datetime_with_timezone(tzp):
    assert vDDDTypes.from_ical("20010101T123000Z") == tzp.localize_utc(
        datetime(2001, 1, 1, 12, 30)
    )


def test_timedelta():
    assert vDDDTypes.from_ical("P31D") == timedelta(31)
    assert vDDDTypes.from_ical("-P31D") == timedelta(-31)


def test_bad_input():
    with pytest.raises(TypeError):
        vDDDTypes(42)


def test_time_from_string():
    assert vDDDTypes.from_ical("123000") == time(12, 30)
    assert isinstance(vDDDTypes.from_ical("123000"), time)


def test_invalid_period_to_ical():
    invalid_period = (datetime(2000, 1, 1), datetime(2000, 1, 2), datetime(2000, 1, 2))
    with pytest.raises(ValueError):
        vDDDTypes(invalid_period).to_ical()


@pytest.mark.parametrize(
    ("value", "expected", "unused_parsers"),
    [
        ("2026-11-08", date(2026, 11, 8), (vDatetime, vTime, vDuration)),
        (
            "2026-11-08T16:52:00",
            datetime(2026, 11, 8, 16, 52),
            (vDate, vTime, vDuration),
        ),
        ("16:52:00", time(16, 52), (vDatetime, vDate, vDuration)),
        ("PT1H", timedelta(hours=1), (vDatetime, vDate, vTime)),
        ("-P1D", timedelta(days=-1), (vDatetime, vDate, vTime)),
        ("+P1D", timedelta(days=1), (vDatetime, vDate, vTime)),
    ],
)
def test_parse_jcal_value_uses_the_matching_parser(
    monkeypatch, value, expected, unused_parsers
):
    """The value format selects the parser, without trial and error."""

    fail = Mock(side_effect=AssertionError("unexpected parser"))

    for parser in unused_parsers:
        monkeypatch.setattr(parser, "parse_jcal_value", fail)
    assert vDDDTypes.parse_jcal_value(value) == expected
