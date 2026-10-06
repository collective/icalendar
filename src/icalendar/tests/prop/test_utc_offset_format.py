from datetime import timedelta

import pytest

from icalendar.prop import vUTCOffset


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0000", timedelta(0)),
        ("0100", timedelta(hours=1)),
        ("1000", timedelta(hours=10)),
        ("0530", timedelta(hours=5, minutes=30)),
        ("013007", timedelta(hours=1, minutes=30, seconds=7)),
        ("+0100", timedelta(hours=1)),
        ("-0500", timedelta(hours=-5)),
        ("+023040", timedelta(hours=2, minutes=30, seconds=40)),
        ("-000030", timedelta(seconds=-30)),
    ],
)
def test_offset_is_read_with_and_without_sign(value, expected):
    assert vUTCOffset.from_ical(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "+",
        "+01",
        "+010",
        "+01000",
        "+0100000",
        " +0100",
        "+0100 ",
        "x0530",
        "Z0100",
        "+01:00",
        "+-100",
        "+٠١٠٠",
        None,
        100,
    ],
)
def test_malformed_offset_is_rejected(value):
    with pytest.raises(ValueError):
        vUTCOffset.from_ical(value)


@pytest.mark.parametrize("value", ["+0160", "+0199", "+010060", "-000099"])
def test_minutes_and_seconds_out_of_range_are_rejected(value):
    with pytest.raises(ValueError):
        vUTCOffset.from_ical(value)


def test_out_of_range_parts_are_kept_when_ignoring_exceptions(
    vUTCOffset_ignore_exceptions,
):
    assert vUTCOffset.from_ical("+0160") == timedelta(hours=2)
    assert vUTCOffset.from_ical("+5744") == timedelta(hours=57, minutes=44)


def test_unsigned_offset_in_timezone_keeps_its_value(calendars):
    calendar = calendars.issue_1885_unsigned_utc_offset
    standard = calendar.timezones[0].subcomponents[0]
    assert standard["TZOFFSETTO"].td == timedelta(hours=1)
    assert b"TZOFFSETTO:+0100\r\n" in calendar.to_ical()
