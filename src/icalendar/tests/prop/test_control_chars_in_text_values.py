r"""TEXT values must reject control characters on parse.

:rfc:`5545#section-3.3.11` defines TEXT as
``*(TSAFE-CHAR / ":" / DQUOTE / ESCAPED-CHAR)`` with
``CONTROL = %x00-08 / %x0A-1F / %x7F``, so control characters other than
the horizontal tab cannot appear in a valid TEXT value. A NUL byte in a
property value previously passed through :meth:`vText.from_ical`
unchanged, and consumers written in C truncate strings at NUL, silently
changing the round-tripped value. TEXT values now reject them like
invalid parameter values do.
"""

import pytest

from icalendar import Calendar, Event, vText
from icalendar.prop import vBroken

FORBIDDEN_VALUES = [
    "A\x00B",  # NUL from the issue report
    "\x00",
    "\x01",
    "\x08",
    "\x0b",  # vertical tab
    "\x0c",  # form feed
    "a\rb",  # lone carriage return
    "\x7f",  # delete
]

VALID_VALUES = [
    "Hello World!",
    'quotes " and colons : and semicolons ; and commas ,',
    r"escapes \; \, \\ stay verbatim here",
    "horizontal tab\tinside",
    "line\nbreak from the escaped sequences",
    "non-US-ASCII: café ☕",
]


@pytest.mark.parametrize("value", FORBIDDEN_VALUES)
def test_vtext_rejects_control_characters(value):
    with pytest.raises(ValueError):
        vText.from_ical(value)


@pytest.mark.parametrize("value", VALID_VALUES)
def test_valid_text_values_still_parse(value):
    assert vText.from_ical(value)


def test_event_collects_nul_in_errors():
    """The invalid line is collected like an invalid parameter value."""
    event = Event.from_ical(b"BEGIN:VEVENT\r\nSUMMARY:A\x00B\r\nEND:VEVENT\r\n")
    assert len(event.errors) == 1
    assert isinstance(event["SUMMARY"], vBroken)


def test_calendar_raises_for_nul_strictly():
    with pytest.raises(ValueError):
        Calendar.from_ical(
            b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:A\x00B\r\nEND:VCALENDAR\r\n"
        )


def test_escaped_newline_still_parses():
    event = Event.from_ical(
        b"BEGIN:VEVENT\r\nSUMMARY:first\\Nsecond\\nthird\r\nEND:VEVENT\r\n"
    )
    assert not event.errors
    assert str(event["SUMMARY"]) == "first\nsecond\nthird"
