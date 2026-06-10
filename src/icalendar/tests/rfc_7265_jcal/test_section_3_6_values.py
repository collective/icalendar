"""Check serialization and deserialization of values.

See https://datatracker.ietf.org/doc/html/rfc7265#section-3.6
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from icalendar import (
    Calendar,
    Event,
    vBinary,
    vBoolean,
    vCalAddress,
    vDate,
    vDatetime,
    vDDDLists,
    vDDDTypes,
    vDuration,
    vFloat,
    vInt,
    vPeriod,
    vRecur,
    vText,
    vTime,
    vUnknown,
    vUri,
    vUTCOffset,
)

JCAL_PAIRS = [
    (["attach", {}, "binary", "SGVsbG8gV29ybGQh"], vBinary("SGVsbG8gV29ybGQh")),
    (["x-non-smoking", {}, "boolean", True], vBoolean(True)),
    (["x-non-smoking", {}, "boolean", False], vBoolean(False)),
    (
        ["attendee", {}, "cal-address", "mailto:kewisch@example.com"],
        vCalAddress("mailto:kewisch@example.com"),
    ),
    (["dtstart", {}, "date", "2011-05-17"], vDate(date(2011, 5, 17))),
    (
        ["dtstart", {}, "date-time", "2012-10-17T12:00:00"],
        vDatetime(datetime(2012, 10, 17, 12, 0, 0)),
    ),
    (
        ["dtstamp", {}, "date-time", "2012-11-17T12:00:00Z"],
        vDatetime(datetime(2012, 11, 17, 12, 0, 0, tzinfo=ZoneInfo("UTC"))),
    ),
    (
        ["dtend", {"tzid": "Europe/Berlin"}, "date-time", "2011-12-17T13:00:00"],
        vDatetime(datetime(2011, 12, 17, 13, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))),
    ),
    (["duration", {}, "duration", "P1D"], vDuration(timedelta(days=1))),
    (["x-grade", {}, "float", 1.3], vFloat(1.3)),
    (["percent-complete", {}, "integer", 42], vInt(42)),
    (["x-foo", {}, "integer", -42], vInt(-42)),
    (
        ["freebusy", {"fbtype": "FREE"}, "period", ["1997-03-08T16:00:00Z", "P1D"]],
        vPeriod(
            (datetime(1997, 3, 8, 16, 0, 0, tzinfo=ZoneInfo("UTC")), timedelta(days=1)),
            params={"fbtype": "FREE"},
        ),
    ),
    (
        [
            "freebusy",
            {"fbtype": "FREE", "tzid": "Europe/Moscow"},
            "period",
            ["1997-03-08T16:00:00", "P1D"],
        ],
        vPeriod(
            (
                datetime(1997, 3, 8, 16, 0, 0, tzinfo=ZoneInfo("Europe/Moscow")),
                timedelta(days=1),
            ),
            params={"fbtype": "FREE"},
        ),
    ),
    (
        [
            "freebusy",
            {"fbtype": "FREE"},
            "period",
            ["1997-03-08T16:00:00", "1997-03-08T16:00:01"],
        ],
        vPeriod(
            (datetime(1997, 3, 8, 16, 0, 0), datetime(1997, 3, 8, 16, 0, 1)),
            params={"fbtype": "FREE"},
        ),
    ),
    (
        [
            "rrule",
            {},
            "recur",
            {"freq": "YEARLY", "count": 5, "byday": ["-1SU", "2MO"], "bymonth": [10]},
        ],
        vRecur({"freq": "YEARLY", "count": 5, "bymonth": 10, "byday": ["-1SU", "2MO"]}),
    ),
    (
        [
            "rrule",
            {},
            "recur",
            {
                "freq": "MONTHLY",
                "interval": 2,
                "bymonthday": [1, 15, -1],
                "until": "2013-10-01",
            },
        ],
        vRecur(
            {
                "freq": "MONTHLY",
                "interval": 2,
                "bymonthday": [1, 15, -1],
                "until": [date(2013, 10, 1)],
            }
        ),
    ),
    (["comment", {}, "text", "hello, world"], vText("hello, world")),
    (["x-time-local", {}, "time", "12:30:00"], vTime(time(hour=12, minute=30))),
    (
        ["x-time-utc", {}, "time", "12:31:00Z"],
        vTime(time(hour=12, minute=31, tzinfo=ZoneInfo("UTC"))),
    ),
    (
        ["x-time-offset", {"tzid": "Europe/Berlin"}, "time", "12:30:00"],
        vTime(time(hour=12, minute=30, tzinfo=ZoneInfo("Europe/Berlin"))),
    ),
    (
        ["tzurl", {}, "uri", "http://example.org/tz/Europe-Berlin.ics"],
        vUri("http://example.org/tz/Europe-Berlin.ics"),
    ),
    (["tzoffsetfrom", {}, "utc-offset", "-05:00"], vUTCOffset(timedelta(hours=-5))),
    (
        ["tzoffsetto", {}, "utc-offset", "+12:45"],
        vUTCOffset(timedelta(hours=12, minutes=45)),
    ),
    (["x-foo", {}, "unknown", "bar"], vUnknown("bar")),
    (
        ["trigger", {}, "date-time", "1976-04-01T00:55:45Z"],
        vDDDTypes(datetime(1976, 4, 1, 0, 55, 45, tzinfo=ZoneInfo("UTC"))),
    ),
]

mark_pairs = pytest.mark.parametrize(("jcal_value", "prop"), JCAL_PAIRS)


@mark_pairs
def test_convert_property_to_jcal(jcal_value, prop):
    """Check converting an icalendar property type into a jCal value"""
    assert prop.to_jcal(jcal_value[0]) == jcal_value


@mark_pairs
def test_convert_jcal_to_property(jcal_value, prop):
    """Check converting an icalendar property type into a jCal value"""
    assert prop.from_jcal(jcal_value) == prop


vDDD_pairs = [  # noqa: N816
    (jcal, prop)
    for jcal, prop in JCAL_PAIRS
    if isinstance(prop, (vDatetime, vDate, vTime, vDuration))
]


@pytest.mark.parametrize(("jcal_value", "prop"), vDDD_pairs)
@pytest.mark.parametrize("ddd_type", [vDDDTypes, vDDDLists])
def test_parse_from_ddd(ddd_type, jcal_value, prop):
    """The DDD types should be able to parse from a jCal value that is of a supported type."""
    parsed = ddd_type.from_jcal(jcal_value)
    print(parsed)
    print(prop, "expected")
    assert parsed == prop


def test_adding_unknown_value_parameter():
    """When converting to iCalendar, [...] the VALUE parameter
    MUST be omitted for properties that have the jCal type identifier
    "unknown"."""
    jcal = ["x-foo", {}, "unknown", "bar"]
    prop = vUnknown.from_jcal(jcal)
    calendar = Calendar()
    calendar["X-FOO"] = prop
    ical = calendar.to_ical().decode("utf-8")
    assert "UNKNOWN" not in ical
    assert "VALUE" not in ical


def test_unknown_jcal_type_does_not_add_value_parameter():
    """The "unknown" jCal type must not produce a VALUE parameter.

    Per :rfc:`7265#section-5.2` a value type of "unknown" yields no VALUE
    parameter, even for a registered property such as DTSTART (whose default
    is DATE-TIME) reached through ``Component.from_jcal``. UNKNOWN is reserved
    from iCalendar.
    """
    jcal = ["vevent", [["uid", {}, "text", "1"], ["dtstart", {}, "unknown", "x"]], []]
    event = Event.from_jcal(jcal)

    assert "VALUE" not in event["DTSTART"].params
    assert b"VALUE=UNKNOWN" not in event.to_ical()


@pytest.mark.parametrize(
    ("ics_line", "prop_name", "expected_value"),
    [
        # Explicit, non-default value types must survive the jCal round-trip.
        ("RDATE;VALUE=PERIOD:19970101T180000Z/19970102T070000Z", "RDATE", "PERIOD"),
        ("TRIGGER;VALUE=DATE-TIME:19760401T005545Z", "TRIGGER", "DATE-TIME"),
        ("DTEND;VALUE=DATE:19961230", "DTEND", "DATE"),
        # Default value types must not gain a spurious VALUE parameter, even for
        # properties whose jCal type differs from the internal type name (such
        # as CATEGORIES, whose jCal type is "text").
        ("DTSTART:19961230T020000Z", "DTSTART", None),
        ("RDATE:19970101T180000Z", "RDATE", None),
        ("TRIGGER:PT15M", "TRIGGER", None),
        ("CATEGORIES:a,b,c", "CATEGORIES", None),
        ("SUMMARY:hello", "SUMMARY", None),
        # Unregistered X- properties: an explicit VALUE must survive, while a
        # bare X- property (jCal type "unknown") must not gain a VALUE parameter
        # -- in particular never the reserved VALUE=UNKNOWN (RFC 7265 section 5.2).
        ("X-FOO;VALUE=DATE:19961230", "X-FOO", "DATE"),
        ("X-FOO:plain text", "X-FOO", None),
    ],
)
def test_jcal_round_trip_preserves_value_parameter(ics_line, prop_name, expected_value):
    """jCal encodes the value type in the type field rather than as a VALUE
    parameter. A round-trip must restore an explicit, non-default VALUE
    parameter and must not introduce one for default value types (GH #1426)."""
    event = Event.from_ical(f"BEGIN:VEVENT\r\n{ics_line}\r\nEND:VEVENT\r\n")
    restored = Event.from_jcal(event.to_jcal())
    prop = restored[prop_name]
    if isinstance(prop, list):
        prop = prop[0]
    assert prop.params.get("VALUE") == expected_value
