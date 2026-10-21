"""Check BASE64 values and conversion to jCal and xCal (issue 1932)."""

import base64

import pytest

from icalendar import Calendar
from icalendar.prop import vBinary, vBroken


def calendar_with_property(content):
    return Calendar.from_ical(
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\n"
        + content
        + "\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    )


@pytest.mark.parametrize("format_name", ["ical", "jcal", "xcal"])
@pytest.mark.parametrize(
    ("property_name", "value"),
    [
        ("SUMMARY", "Hello"),
        ("SUMMARY;LANGUAGE=fr", "Café à Paris"),
        ("DESCRIPTION", r"First\nSecond\, third\; path\\name"),
        ("SUMMARY", ""),
        ("PRIORITY", "3"),
        ("X-NUMBER;VALUE=FLOAT", "1.5"),
        ("X-BOOL;VALUE=BOOLEAN", "TRUE"),
        ("DTSTART;VALUE=DATE", "20261021"),
        ("DTSTART;TZID=Europe/Berlin", "20261021T103000"),
        ("DURATION", "PT1H"),
        ("RRULE", "FREQ=DAILY;COUNT=2"),
        ("CATEGORIES;LANGUAGE=en", r"work\,home,call:team,path\\name"),
        ("RDATE;VALUE=DATE", "20261021,20261022"),
        ("EXDATE;VALUE=DATE", "20261021,20261022"),
        ("FREEBUSY", "20261021T100000Z/PT1H,20261022T100000Z/PT2H"),
        ("URL", "https://example.org/a%2Fb"),
        ("X-OPAQUE", r"one\ntwo\,three;%2F"),
    ],
)
def test_non_binary_base64_conversion(property_name, value, format_name):
    expected = calendar_with_property(f"{property_name}:{value}")
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    calendar = calendar_with_property(f"{property_name};ENCODING=BASE64:{encoded}")
    assert calendar.to_ical() == expected.to_ical()

    serialized = getattr(calendar, f"to_{format_name}")()
    assert serialized == getattr(expected, f"to_{format_name}")()


@pytest.mark.parametrize("format_name", ["ical", "jcal", "xcal"])
def test_base64_text_round_trip(format_name):
    value = r"Café\nCall\, team\; path\\name"
    expected = calendar_with_property(f"DESCRIPTION;LANGUAGE=fr:{value}")
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    calendar = calendar_with_property(
        f"DESCRIPTION;LANGUAGE=fr;ENCODING=BASE64:{encoded}"
    )
    serialized = getattr(calendar, f"to_{format_name}")()
    restored = getattr(Calendar, f"from_{format_name}")(serialized)
    if format_name == "xcal":
        restored = restored[0]
    assert restored.to_ical() == expected.to_ical()


def test_base64_preserves_quoted_parameters_and_text():
    value = "Café, call:team"
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    calendar = calendar_with_property(
        'SUMMARY;ALTREP="https://example.org/a:b";LANGUAGE=fr;'
        f"ENCODING=BASE64:{encoded}"
    )
    summary = calendar.events[0]["SUMMARY"]
    assert summary == value
    assert summary.params == {"ALTREP": "https://example.org/a:b", "LANGUAGE": "fr"}


@pytest.mark.parametrize("encoding", ["BASE64", "base64", "BaSe64"])
def test_base64_parameter_is_case_insensitive(encoding):
    calendar = calendar_with_property(f"SUMMARY;ENCODING={encoding}:SGVsbG8=")
    assert calendar.events[0]["SUMMARY"] == "Hello"
    assert "ENCODING" not in calendar.events[0]["SUMMARY"].params


def test_folded_base64_text():
    value = "Café " * 40
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    folded = "\r\n ".join(encoded[i : i + 40] for i in range(0, len(encoded), 40))
    calendar = calendar_with_property(f"SUMMARY;ENCODING=BASE64:{folded}")
    assert calendar.events[0]["SUMMARY"] == value


@pytest.mark.parametrize("value", ["SGVsbG8", "!!!", "é", "/w=="])
def test_invalid_base64_uses_tolerant_error_handling(value):
    calendar = calendar_with_property(
        f"SUMMARY;ENCODING=BASE64:{value}\r\nLOCATION:Elsewhere"
    )
    event = calendar.events[0]
    assert isinstance(event["SUMMARY"], vBroken)
    assert event["SUMMARY"].params["ENCODING"] == "BASE64"
    assert event.errors
    assert event["LOCATION"] == "Elsewhere"


@pytest.mark.parametrize("value", ["SGVsbG8", "!!!", "é", "/w=="])
def test_invalid_base64_uses_strict_error_handling(value):
    with pytest.raises(ValueError):
        Calendar.from_ical(
            f"BEGIN:VCALENDAR\r\nPRODID;ENCODING=BASE64:{value}\r\nEND:VCALENDAR"
        )


@pytest.mark.parametrize("format_name", ["ical", "jcal", "xcal"])
@pytest.mark.parametrize("value", [b"SGVsbG8=", bytes(range(256))])
def test_binary_is_decoded_once(value, format_name):
    encoded = base64.b64encode(value).decode("ascii")
    calendar = calendar_with_property(
        f"ATTACH;VALUE=BINARY;ENCODING=BASE64;FMTTYPE=application/octet-stream:{encoded}"
    )
    attachment = calendar.events[0]["ATTACH"]
    assert isinstance(attachment, vBinary)
    assert attachment.bytes == value
    serialized = getattr(calendar, f"to_{format_name}")()
    restored = getattr(Calendar, f"from_{format_name}")(serialized)
    if format_name == "xcal":
        restored = restored[0]
    attachment = restored.events[0]["ATTACH"]
    assert attachment.bytes == value
    assert attachment.params["FMTTYPE"] == "application/octet-stream"


def test_unencoded_text_is_unchanged():
    calendar = calendar_with_property("SUMMARY;ENCODING=8BIT:SGVsbG8=")
    assert calendar.events[0]["SUMMARY"] == "SGVsbG8="
    assert calendar.events[0]["SUMMARY"].params["ENCODING"] == "8BIT"
