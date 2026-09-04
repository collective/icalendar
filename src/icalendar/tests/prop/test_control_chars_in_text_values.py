r"""TEXT values must reject control characters on parse.

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

A NUL byte in a property value previously passed through :meth:`vText.from_ical`
unchanged, and consumers written in C truncate strings at NUL, silently
changing the round-tripped value. TEXT values now reject them like
invalid parameter values do.
"""

import pytest

from icalendar import Calendar, Event, vText
from icalendar.prop import vBroken

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
