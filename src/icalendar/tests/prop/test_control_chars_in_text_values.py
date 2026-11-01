r"""TEXT values must not emit control characters.

:rfc:`5545#section-3.3.11` defines TEXT as
``*(TSAFE-CHAR / ":" / DQUOTE / ESCAPED-CHAR)`` where TSAFE-CHAR is defined by
the following grammar.

..  code-block:: text

    TSAFE-CHAR = WSP / %x21 / %x23-2B / %x2D-39 / %x3C-5B /
             %x5D-7E / NON-US-ASCII
       ; Any character except CONTROLs not needed by the current
       ; character set, DQUOTE, ";", ":", "\", ","

In turn, CONTROL is defined by the following grammar in :rfc:`5545#section-3.1`.

..  code-block:: text

    CONTROL       = %x00-08 / %x0A-1F / %x7F
    ; All the controls except HTAB

Although "the current character set" may be one of many, it is UTF-8 by default
per :rfc:`5545#section-3.1.4`. Thus TEXT should reject all the CONTROLs except
the horizontal tab, ``%x09``. Additionally the new line, ``%x0A``, is needed by
the current character set because it is the result of the escaped sequences
``\N`` and ``\n``.

A NUL byte in a property value previously passed through to ``to_ical()``.
Consumers written in C truncate strings at NUL, silently changing the
round-tripped value. Parsing stays open so problematic files can still be
read; :class:`~icalendar.prop.text.vText` removes leftover CONTROLs when
constructed so both ``to_ical`` and ``to_jcal`` stay valid. Parameter values
still reject NUL into ``component.errors``.
"""

import uuid

import pytest

from icalendar import Calendar, Event, vText, vUid
from icalendar.prop.text import _UNSAFE_TEXT_CHARS

#: Every CONTROL from :rfc:`5545#section-3.1`. The horizontal tab, ``%x09``,
#: is not a CONTROL, and the new line, ``%x0A``, is not forbidden because the
#: escaped sequences ``\N`` and ``\n`` produce it.
FORBIDDEN_CONTROL_CHARS = [
    chr(control) for control in range(0x20) if control not in (0x09, 0x0A)
] + ["\x7f"]

FORBIDDEN_VALUES = [
    *FORBIDDEN_CONTROL_CHARS,
    "A\x00B",  # NUL from the issue report
    "a\rb",  # lone carriage return
    "a\x01b",  # SOH
    "a\x7fb",  # DEL
]

VALID_VALUES = [
    "Hello World!",
    'quotes " and colons : and semicolons ; and commas ,',
    r"escapes \; \, \\ stay verbatim here",
    "horizontal tab\tinside",
    "horizontal tab as hex\x09inside",
    "newline\nfrom the escaped sequences",
    "non-US-ASCII: café ☕",
]


def _contains_forbidden_control(data: str | bytes) -> bool:
    if isinstance(data, bytes):
        return any(ch.encode("latin-1") in data for ch in FORBIDDEN_CONTROL_CHARS)
    return any(ch in data for ch in FORBIDDEN_CONTROL_CHARS)


@pytest.mark.parametrize("codepoint", range(128))
def test_unsafe_text_chars_matches_forbidden_ascii(codepoint):
    ch = chr(codepoint)
    if ch in FORBIDDEN_CONTROL_CHARS:
        assert _UNSAFE_TEXT_CHARS.search(ch)
    else:
        assert _UNSAFE_TEXT_CHARS.search(ch) is None


@pytest.mark.parametrize("value", FORBIDDEN_VALUES)
def test_vtext_from_ical_stays_open(value):
    parsed = vText.from_ical(value)
    assert not _contains_forbidden_control(parsed)


@pytest.mark.parametrize("value", FORBIDDEN_VALUES)
def test_vtext_to_ical_strips_control_characters(value):
    serialized = vText(value).to_ical()
    assert not _contains_forbidden_control(serialized)


@pytest.mark.parametrize("value", FORBIDDEN_VALUES)
def test_vtext_to_jcal_strips_control_characters(value):
    jcal = vText(value).to_jcal("summary")
    assert not _contains_forbidden_control(jcal[3])


@pytest.mark.parametrize("value", VALID_VALUES)
def test_valid_text_values_still_parse(value):
    assert vText.from_ical(value) == value


@pytest.mark.parametrize("value", VALID_VALUES)
def test_valid_text_values_still_serialize(value):
    serialized = vText(value).to_ical()
    assert not _contains_forbidden_control(serialized)


def test_reporter_repro_does_not_emit_nul():
    event = Event.from_ical(b"BEGIN:VEVENT\r\nSUMMARY:A\x00B\r\nEND:VEVENT\r\n")
    assert not event.errors
    assert str(event["SUMMARY"]) == "AB"
    assert b"\x00" not in event.to_ical()
    assert b"SUMMARY:AB" in event.to_ical()


def test_constructed_event_does_not_emit_nul():
    event = Event()
    event.add("SUMMARY", "A\x00B")
    assert str(event["SUMMARY"]) == "AB"
    assert b"\x00" not in event.to_ical()
    assert b"SUMMARY:AB" in event.to_ical()


def test_calendar_prodid_with_nul_parses_and_sanitizes():
    calendar = Calendar.from_ical(
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:A\x00B\r\nEND:VCALENDAR\r\n"
    )
    assert not calendar.errors
    assert str(calendar["PRODID"]) == "AB"
    assert b"\x00" not in calendar.to_ical()


def test_lone_cr_becomes_newline_not_stripped():
    text = vText.from_ical("a\rb")
    assert str(text) == "a\nb"
    assert text.to_ical() == rb"a\nb"


def test_escaped_newline_still_parses():
    event = Event.from_ical(
        b"BEGIN:VEVENT\r\nSUMMARY:first\\Nsecond\\nthird\r\nEND:VEVENT\r\n"
    )
    assert not event.errors
    assert str(event["SUMMARY"]) == "first\nsecond\nthird"
    assert b"SUMMARY:first\\nsecond\\nthird" in event.to_ical()


def test_parameter_nul_still_collected_in_errors():
    """The parameter path still rejects NUL into ``errors``."""
    event = Event.from_ical(
        b"BEGIN:VEVENT\r\nSUMMARY;LANGUAGE=en\x00:Hello\r\nEND:VEVENT\r\n"
    )
    assert event.errors


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, "1"),
        (None, "None"),
        (
            uuid.UUID("d755cef5-2311-46ed-a0e1-6733c9e15c63"),
            "d755cef5-2311-46ed-a0e1-6733c9e15c63",
        ),
    ],
)
def test_vtext_coerces_non_string_constructor_values(value, expected):
    """to_unicode leaves UUID/int/None as-is; construction must still work."""
    text = vText(value)
    assert str(text) == expected
    assert not _contains_forbidden_control(text.to_ical())


def test_vuid_new_and_event_new_accept_uuid():
    uid = vUid.new()
    assert str(uid)
    assert not _contains_forbidden_control(uid.to_ical())
    event = Event.new()
    assert event.uid
    assert b"\x00" not in event.to_ical()
