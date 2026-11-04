"""UTC offsets without a sign are no longer read as the wrong value.

RFC 5545, section 3.3.14, writes a UTC offset as a sign, two digits for the
hours, two for the minutes and two optional ones for the seconds.
``vUTCOffset.from_ical`` used to take the first character as the sign without
looking at it, so ``0100`` was read as ten hours and ``x0530`` was accepted.

The value is now matched as a whole against a pattern. A missing sign and any
other wrong shape raise an ``ICalParsingError``, and a value that is not a
string raises a ``TypeError``. If ``vUTCOffset.ignore_exceptions`` is ``True``,
a missing sign is read as positive.

See https://github.com/collective/icalendar/issues/1885
"""

import re
from datetime import timedelta

import pytest

from icalendar.error import ICalParsingError
from icalendar.prop import vUTCOffset


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("+0100", timedelta(hours=1)),
        ("+1000", timedelta(hours=10)),
        ("+0530", timedelta(hours=5, minutes=30)),
        ("-0500", timedelta(hours=-5)),
        ("+023040", timedelta(hours=2, minutes=30, seconds=40)),
        ("-000030", timedelta(seconds=-30)),
    ],
)
def test_offset_with_sign_is_read(value, expected):
    assert vUTCOffset.from_ical(value) == expected


UNSIGNED_OFFSETS = [
    ("0000", timedelta(0)),
    ("0100", timedelta(hours=1)),
    ("1000", timedelta(hours=10)),
    ("0530", timedelta(hours=5, minutes=30)),
    ("2359", timedelta(hours=23, minutes=59)),
    ("013007", timedelta(hours=1, minutes=30, seconds=7)),
    ("235959", timedelta(hours=23, minutes=59, seconds=59)),
]


@pytest.mark.parametrize("value", [value for value, _ in UNSIGNED_OFFSETS])
def test_offset_without_sign_is_rejected(value):
    message = f"UTC offset must have a sign (+ or -): {value!r}"
    with pytest.raises(ICalParsingError, match=re.escape(message)):
        vUTCOffset.from_ical(value)


@pytest.mark.parametrize(("value", "expected"), UNSIGNED_OFFSETS)
def test_offset_without_sign_is_positive_when_ignoring_exceptions(
    value, expected, vUTCOffset_ignore_exceptions
):
    assert vUTCOffset.from_ical(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("+0000", timedelta(0)),
        ("+000000", timedelta(0)),
        ("+0059", timedelta(minutes=59)),
        ("+000059", timedelta(seconds=59)),
        ("+2359", timedelta(hours=23, minutes=59)),
        ("-2359", -timedelta(hours=23, minutes=59)),
        ("+235959", timedelta(hours=23, minutes=59, seconds=59)),
        ("-235959", -timedelta(hours=23, minutes=59, seconds=59)),
        ("+000060", timedelta(seconds=60)),
        ("-000060", timedelta(seconds=-60)),
        ("+010060", timedelta(hours=1, seconds=60)),
        ("+235860", timedelta(hours=23, minutes=59)),
    ],
)
def test_largest_and_smallest_offsets_are_read(value, expected):
    assert vUTCOffset.from_ical(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "1",
        "11",
        "111",
        "11111",
        "1111111",
        "x222",
        "x2222",
        "+",
        "+01",
        "+010",
        "+01000",
        "+0100000",
        " +0100",
        "+0100 ",
        "+0100\n",
        "x0530",
        "Z0100",
        "+01:00",
        "+-100",
        "++0100",
        "+٠١٠٠",
    ],
)
def test_malformed_offset_is_rejected(value):
    message = f"Expected UTC offset as [+-]HHMM[SS]: {value!r}"
    with pytest.raises(ICalParsingError, match=re.escape(message)):
        vUTCOffset.from_ical(value)


@pytest.mark.parametrize("value", ["+2400", "-2400", "+240000", "+9959", "+235960"])
def test_offset_of_24_hours_or_more_is_rejected(value):
    message = f"UTC offset must be less than 24 hours: {value!r}"
    with pytest.raises(ICalParsingError, match=re.escape(message)):
        vUTCOffset.from_ical(value)


@pytest.mark.parametrize(
    "value", ["+0160", "+0199", "-0160", "+016000", "+010061", "-000061", "-000099"]
)
def test_minutes_and_seconds_out_of_range_are_rejected(value):
    message = (
        "UTC offset minutes must be less than 60 "
        f"and seconds less than or equal to 60: {value!r}"
    )
    with pytest.raises(ICalParsingError, match=re.escape(message)):
        vUTCOffset.from_ical(value)


@pytest.mark.parametrize(
    ("value", "type_name"),
    [
        (None, "NoneType"),
        (100, "int"),
        (b"+0100", "bytes"),
        (timedelta(hours=1), "timedelta"),
    ],
)
def test_value_that_is_not_a_string_raises_type_error(value, type_name):
    message = f"UTC offset must be a str or vUTCOffset, not {type_name}"
    with pytest.raises(TypeError, match=re.escape(message)):
        vUTCOffset.from_ical(value)


def test_out_of_range_parts_are_kept_when_ignoring_exceptions(
    vUTCOffset_ignore_exceptions,
):
    assert vUTCOffset.from_ical("+0160") == timedelta(hours=2)
    assert vUTCOffset.from_ical("+5744") == timedelta(hours=57, minutes=44)


def test_unsigned_offset_in_timezone_is_rejected(calendars):
    message = "UTC offset must have a sign (+ or -): '0100'"
    with pytest.raises(ICalParsingError, match=re.escape(message)):
        calendars.issue_1885_unsigned_utc_offset.timezones[0].subcomponents


def test_unsigned_offset_in_timezone_keeps_its_value_when_ignoring_exceptions(
    calendars, vUTCOffset_ignore_exceptions
):
    calendar = calendars.issue_1885_unsigned_utc_offset
    standard = calendar.timezones[0].subcomponents[0]
    assert standard["TZOFFSETTO"].td == timedelta(hours=1)
    assert b"TZOFFSETTO:+0100\r\n" in calendar.to_ical()
