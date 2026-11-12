"""Tests for NFC normalization of component text properties on read."""

import unicodedata

from icalendar import Calendar, Event
from icalendar.prop import vText

NFD = "cafe\u0301"  # "e" + combining acute accent
NFC = "caf\u00e9"  # precomposed "é"


def test_multi_language_text_properties_are_nfc():
    """Attributes backed by multi_language_text_property return NFC strings."""
    event = Event()
    event["SUMMARY"] = NFD
    event["DESCRIPTION"] = NFD
    event["LOCATION"] = NFD

    assert event.summary == NFC
    assert event.description == NFC
    assert event.location == NFC
    assert unicodedata.is_normalized("NFC", event.summary)

    cal = Calendar()
    cal["NAME"] = NFD
    assert cal.calendar_name == NFC


def test_language_parameter_survives_normalization():
    """vText params like LANGUAGE are preserved through getter normalization."""
    event = Event()
    event["SUMMARY"] = vText(NFD, params={"LANGUAGE": "fr"})

    summary = event.summary
    assert summary == NFC
    assert isinstance(summary, vText)
    assert summary.params.get("LANGUAGE") == "fr"


def test_multi_text_properties_are_nfc():
    """Attributes backed by multi_text_property return NFC strings."""
    event = Event()
    event.add("COMMENT", NFD)
    event.add("CONTACT", NFD)

    assert event.comments == [NFC]
    assert event.contacts == [NFC]


def test_identifiers_are_left_alone():
    """UID, PRODID, and URL must NOT be altered or normalized."""
    event = Event()
    event["UID"] = NFD
    assert event["UID"] == NFD

    cal = Calendar()
    cal["PRODID"] = NFD
    assert cal["PRODID"] == NFD


def test_round_trip_keeps_original_bytes():
    """to_ical() must keep the original raw bytes without mutating them to NFC."""
    raw_ics = (
        b"BEGIN:VCALENDAR\r\n"
        b"VERSION:2.0\r\n"
        b"PRODID:-//Example//EN\r\n"
        b"BEGIN:VEVENT\r\n"
        b"UID:12345\r\n"
        b"SUMMARY:" + NFD.encode("utf-8") + b"\r\n"
        b"END:VEVENT\r\n"
        b"END:VCALENDAR\r\n"
    )
    cal = Calendar.from_ical(raw_ics)
    event = cal.events[0]

    # The getter returns NFC for consumption in Python:
    assert event.summary == NFC

    # But to_ical() preserves the original raw NFD bytes from the file:
    assert NFD.encode("utf-8") in cal.to_ical()
