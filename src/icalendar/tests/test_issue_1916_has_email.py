"""Match calendar addresses and their EMAIL parameters."""

import pytest

from icalendar import Event, vCalAddress


@pytest.mark.parametrize("prefix", ["", "mailto:", "MAILTO:"])
@pytest.mark.parametrize("email", ["person@example.com", "PERSON@EXAMPLE.COM"])
@pytest.mark.parametrize(
    ("value", "parameter"),
    [
        ("mailto:person@example.com", None),
        ("PERSON@EXAMPLE.COM", None),
        ("urn:uuid:calendar-user", "person@example.com"),
        ("mailto:other@example.com", "MAILTO:PERSON@EXAMPLE.COM"),
    ],
)
def test_has_email_matches_either_address(value, parameter, prefix, email):
    """Both sources match regardless of case or a mailto prefix."""
    address = vCalAddress(value)
    address.EMAIL = parameter

    assert address.has_email(prefix + email)
    assert not address.has_email("unrelated@example.com")


def test_has_email_checks_both_addresses_when_email_parameter_is_set():
    """An EMAIL parameter does not hide the calendar address."""
    address = vCalAddress("mailto:calendar@example.com")
    address.EMAIL = "contact@example.com"

    assert address.has_email("calendar@example.com")
    assert address.has_email("contact@example.com")


@pytest.mark.parametrize("stored", ["straße@example.com", "STRASSE@example.com"])
@pytest.mark.parametrize("query", ["straße@example.com", "STRASSE@example.com"])
@pytest.mark.parametrize("use_parameter", [False, True])
def test_has_email_matches_unicode_case_variants(stored, query, use_parameter):
    """Case-insensitive matching handles Unicode in both address sources."""
    if use_parameter:
        address = vCalAddress("urn:uuid:calendar-user")
        address.EMAIL = stored
    else:
        address = vCalAddress("mailto:" + stored)

    assert address.has_email("MAILTO:" + query)
    assert not address.has_email("other@example.com")


def test_has_email_uses_current_parameter():
    """Changing or deleting EMAIL updates which contact address matches."""
    address = vCalAddress("mailto:calendar@example.com")
    address.EMAIL = "old@example.com"
    assert address.has_email("old@example.com")

    address.EMAIL = "new@example.com"
    assert not address.has_email("old@example.com")
    assert address.has_email("new@example.com")

    del address.EMAIL
    assert not address.has_email("new@example.com")
    assert address.has_email("calendar@example.com")


def test_has_email_does_not_match_an_absent_parameter():
    """A missing EMAIL parameter must not act like an empty address."""
    address = vCalAddress("urn:uuid:calendar-user")

    assert not address.has_email("")
    assert not address.has_email("person@example.com")


@pytest.mark.parametrize("property_name", ["ATTENDEE", "ORGANIZER"])
def test_has_email_after_calendar_round_trip(property_name):
    """Parsed calendar users match both stored addresses."""
    address = vCalAddress("mailto:calendar@example.com")
    address.EMAIL = "contact@example.com"
    event = Event()
    event.add(property_name, address)

    parsed = Event.from_ical(event.to_ical())[property_name]

    assert parsed.has_email("MAILTO:CALENDAR@EXAMPLE.COM")
    assert parsed.has_email("CONTACT@EXAMPLE.COM")
    assert not parsed.has_email("unrelated@example.com")
