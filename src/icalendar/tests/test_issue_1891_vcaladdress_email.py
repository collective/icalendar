"""Tests for the RFC 7986 EMAIL parameter."""

import pytest

from icalendar import Event, vCalAddress


def test_email_parameter_is_distinct_from_calendar_address():
    address = vCalAddress("mailto:opaque-token@example.com")

    assert address.EMAIL is None

    address.EMAIL = "person@example.com"

    assert address.EMAIL == "person@example.com"
    assert address.email == "opaque-token@example.com"
    assert address.params["EMAIL"] == "person@example.com"


def test_email_parameter_can_be_removed():
    address = vCalAddress(
        "mailto:opaque-token@example.com",
        params={"EMAIL": "person@example.com"},
    )

    address.EMAIL = None
    assert address.EMAIL is None
    assert "EMAIL" not in address.params

    address.EMAIL = "person@example.com"
    del address.EMAIL
    assert address.EMAIL is None
    assert "EMAIL" not in address.params


@pytest.mark.parametrize("property_name", ["ATTENDEE", "ORGANIZER"])
def test_email_parameter_round_trip(property_name: str):
    address = vCalAddress("mailto:opaque-token@example.com")
    address.EMAIL = "person@example.com"
    event = Event()
    event.add(property_name, address)

    serialized = event.to_ical()
    assert f"{property_name};EMAIL=person@example.com:".encode() in serialized

    parsed = Event.from_ical(serialized)
    parsed_address = parsed[property_name]
    assert isinstance(parsed_address, vCalAddress)
    assert parsed_address.EMAIL == "person@example.com"
    assert parsed_address.email == "opaque-token@example.com"
