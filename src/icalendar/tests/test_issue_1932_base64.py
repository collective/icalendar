"""Check BASE64 decoding with shared calendar fixtures (issue 1932)."""

import pytest

from icalendar import Base64DecodingError, Event, ICalParsingError
from icalendar.prop import vBinary, vBroken


@pytest.mark.parametrize(
    ("case", "property_name"),
    [
        ("text", "SUMMARY"),
        ("utf8", "SUMMARY"),
        ("escapes", "DESCRIPTION"),
        ("empty-text", "SUMMARY"),
        ("integer", "PRIORITY"),
        ("date", "DTSTART"),
        ("timezone", "DTSTART"),
        ("duration", "DURATION"),
        ("recurrence", "RRULE"),
        ("categories", "CATEGORIES"),
        ("rdate", "RDATE"),
        ("exdate", "EXDATE"),
        ("freebusy", "FREEBUSY"),
        ("uri", "URL"),
        ("unknown", "X-OPAQUE"),
        ("empty-unknown", "X-OPAQUE"),
        ("quoted-params", "SUMMARY"),
        ("folded", "SUMMARY"),
        ("8bit", "SUMMARY"),
        ("repeated-encoding", "SUMMARY"),
        ("encoding-list", "SUMMARY"),
        ("binary-once", "ATTACH"),
        ("binary-bytes", "ATTACH"),
        ("empty-binary", "ATTACH"),
    ],
)
def test_base64_matches_plain_values(calendars, case, property_name):
    encoded = calendars.issue_1932_base64
    plain = calendars.issue_1932_plain
    actual = next(event for event in encoded.events if event["UID"] == case)
    expected = next(event for event in plain.events if event["UID"] == case)
    assert type(actual[property_name]) is type(expected[property_name])
    assert actual[property_name] == expected[property_name]
    assert actual.to_ical() == expected.to_ical()


@pytest.mark.parametrize("format_name", ["ical", "jcal", "xcal"])
def test_base64_custom_value_conversion(calendars, format_name):
    """Compare custom types; xCal does not yet retain their VALUE parameter."""
    encoded = calendars["issue_1932/custom_encoded"]
    plain = calendars["issue_1932/custom_plain"]
    assert (
        getattr(encoded, f"to_{format_name}")() == getattr(plain, f"to_{format_name}")()
    )


@pytest.mark.parametrize(
    ("case", "value"),
    [
        ("binary-once", b"SGVsbG8="),
        ("binary-bytes", bytes(range(256))),
        ("empty-binary", b""),
    ],
)
def test_base64_binary_bytes(calendars, case, value):
    event = next(
        event for event in calendars.issue_1932_base64.events if event["UID"] == case
    )
    attachment = event["ATTACH"]
    assert isinstance(attachment, vBinary)
    assert attachment.bytes == value
    assert attachment.params == {
        "VALUE": "BINARY",
        "ENCODING": "BASE64",
        "FMTTYPE": "application/octet-stream",
    }


@pytest.mark.parametrize(
    ("case", "property_name", "value", "message"),
    [
        ("text-padding", "SUMMARY", "SGVsbG8", "Not valid base 64 encoding."),
        ("text-alphabet", "SUMMARY", "!!!", "Not valid base 64 encoding."),
        ("text-ascii", "SUMMARY", "é", "Not valid base 64 encoding."),
        (
            "text-utf8",
            "SUMMARY",
            "/w==",
            "BASE64 data is not valid UTF-8: '/w=='",
        ),
        ("binary-padding", "ATTACH", "SGVsbG8", "Not valid base 64 encoding."),
        ("binary-alphabet", "ATTACH", "!!!", "Not valid base 64 encoding."),
        ("binary-ascii", "ATTACH", "é", "Not valid base 64 encoding."),
    ],
)
def test_base64_errors(calendars, monkeypatch, case, property_name, value, message):
    event = next(
        event
        for event in calendars.issue_1932_invalid_base64.events
        if event["UID"] == case
    )
    broken = event[property_name]
    assert isinstance(broken, vBroken)
    assert broken == value
    assert broken.params["ENCODING"] == "BASE64"
    assert isinstance(broken.parse_error, Base64DecodingError)
    assert isinstance(broken.parse_error, ICalParsingError)
    assert str(broken.parse_error) == message
    assert event.errors == [(property_name, message)]
    assert event["LOCATION"] == "Elsewhere"

    monkeypatch.setattr(Event, "ignore_exceptions", False)
    with pytest.raises(Base64DecodingError) as error:
        Event.from_ical(event.to_ical())
    assert str(error.value) == message
